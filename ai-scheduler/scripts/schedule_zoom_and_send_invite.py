import argparse
import base64
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr
from html import escape as html_escape
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from agentmail import AgentMail
    from agentmail.attachments.types.send_attachment import SendAttachment
except Exception:
    AgentMail = None  # type: ignore[assignment]
    SendAttachment = None  # type: ignore[assignment]


ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE = "https://api.zoom.us/v2"


def _require_httpx():
    try:
        import httpx  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "httpx is not installed in this Python environment. "
            "Install it or run this script from your configured venv."
        ) from e
    return httpx


@dataclass(frozen=True)
class ZoomMeeting:
    meeting_id: int
    join_url: str
    start_time: str
    timezone: str
    password: str | None


@dataclass(frozen=True)
class Participant:
    name: str | None
    email: str


def ics_quote_param_value(value: str) -> str:
    v = (value or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{v}"'


def format_zoom_meeting_id(meeting_id: int) -> str:
    s = str(meeting_id)
    if len(s) == 11:
        return f"{s[0:3]} {s[3:7]} {s[7:11]}"
    if len(s) == 10:
        return f"{s[0:3]} {s[3:6]} {s[6:10]}"
    return s


def _format_participant(p: Participant) -> str:
    if p.name:
        return f"{p.name} <{p.email}>"
    return p.email


def parse_participants(value: str | None) -> list[Participant]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",")]
    participants: list[Participant] = []
    for raw in parts:
        if not raw:
            continue
        name, email = parseaddr(raw)
        email = (email or "").strip()
        name = (name or "").strip() or None
        if not email:
            continue
        participants.append(Participant(name=name, email=email))
    return participants


def merge_participants(primary: list[Participant], extra: list[Participant]) -> list[Participant]:
    if not extra:
        return list(primary)
    seen = {p.email.lower() for p in primary}
    merged = list(primary)
    for p in extra:
        key = p.email.lower()
        if key in seen:
            continue
        merged.append(p)
        seen.add(key)
    return merged


def normalize_topic(topic: str, *, subject_prefix: str | None) -> str:
    t = (topic or "").strip()
    if not t:
        return "Zoom Meeting"
    prefix = (subject_prefix or "").strip()
    if prefix:
        prefix_with_space = f"{prefix} "
        if t.startswith(prefix_with_space):
            t = t[len(prefix_with_space) :].strip()
    return t or "Zoom Meeting"


def compact_topic(topic: str, *, max_words: int = 5) -> str:
    words = [w for w in (topic or "").strip().split() if w]
    if not words:
        return "Zoom Meeting"
    return " ".join(words[:max_words])


def format_subject(*, topic: str, to_participants: list[Participant], subject_prefix: str | None) -> str:
    compact = compact_topic(topic, max_words=5)
    prefix = (subject_prefix or "").strip()
    if len(to_participants) == 1:
        display = to_participants[0].name or to_participants[0].email
        if prefix:
            return f"{prefix} {display}: {compact}"
        return f"{display}: {compact}"
    if prefix:
        return f"{prefix} {compact}"
    return compact


def format_subject_topic_only(*, topic: str, subject_prefix: str | None) -> str:
    compact = compact_topic(topic, max_words=5)
    prefix = (subject_prefix or "").strip()
    if prefix:
        return f"{prefix} {compact}"
    return compact


def sanitize_zoom_topic(value: str) -> str:
    allowed_punct = {"+", ":", "$", "-", "–", "—", "·", "&", "'", "(", ")"}
    cleaned = []
    for ch in (value or ""):
        if ch.isalnum() or ch.isspace() or ch in allowed_punct:
            cleaned.append(ch)
        else:
            cleaned.append(" ")
    topic = " ".join("".join(cleaned).split())
    return topic or "Zoom Meeting"


def print_confirmation_summary(
    *,
    from_email: str,
    to_participants: list[Participant],
    cc_participants: list[Participant],
    start_local: datetime,
    end_local: datetime,
    timezone_name: str,
    subject: str,
) -> None:
    date_human = f"{start_local.strftime('%B')} {start_local.day}, {start_local.year}"
    time_start = start_local.strftime("%I:%M %p").lstrip("0")
    time_end = end_local.strftime("%I:%M %p").lstrip("0")

    print("")
    print("Confirm before sending:")
    print(" - from:", from_email)
    print(" - to:", [_format_participant(p) for p in to_participants])
    print(" - cc:", [_format_participant(p) for p in cc_participants])
    print(" - when:", f"{date_human} · {time_start} – {time_end} ({timezone_name})")
    print(" - subject:", subject)
    print("")


def print_email_preview(*, subject: str, body_text: str) -> None:
    print("Email preview:")
    print(" - subject:", subject)
    print("")
    print(body_text.rstrip("\n"))
    print("")


def confirm_or_exit() -> None:
    resp = input("Send invite email? [y/N] ").strip().lower()
    if resp not in {"y", "yes"}:
        raise SystemExit("Canceled.")


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value


def load_env_file(path: str) -> None:
    env_path = Path(path).expanduser()
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def zoom_access_token(*, account_id: str, client_id: str, client_secret: str) -> str:
    httpx = _require_httpx()
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    headers = {"Authorization": f"Basic {basic}"}
    params = {"grant_type": "account_credentials", "account_id": account_id}
    with httpx.Client(timeout=30) as client:
        resp = client.post(ZOOM_TOKEN_URL, params=params, headers=headers)
        if resp.status_code >= 400:
            raise RuntimeError(f"Zoom token error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Zoom token response missing access_token")
    return token


def create_zoom_meeting(
    *,
    token: str,
    topic: str,
    start_dt: datetime,
    duration_minutes: int,
    timezone_name: str,
    agenda: str | None,
) -> ZoomMeeting:
    httpx = _require_httpx()
    headers = {"Authorization": f"Bearer {token}"}
    payload: dict[str, object] = {
        "topic": topic,
        "type": 2,
        "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": duration_minutes,
        "timezone": timezone_name,
    }
    if agenda:
        payload["agenda"] = agenda

    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{ZOOM_API_BASE}/users/me/meetings", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    meeting_id = data.get("id")
    join_url = data.get("join_url")
    start_time = data.get("start_time")
    tz = data.get("timezone") or timezone_name
    password = data.get("password")
    if not meeting_id or not join_url or not start_time:
        raise RuntimeError(f"Unexpected Zoom create meeting response: {data}")
    return ZoomMeeting(
        meeting_id=int(meeting_id),
        join_url=str(join_url),
        start_time=str(start_time),
        timezone=str(tz),
        password=str(password) if password else None,
    )


def build_ics(
    *,
    organizer_email: str,
    organizer_name: str,
    to_participants: list[Participant],
    cc_participants: list[Participant],
    topic: str,
    start_local: datetime,
    end_local: datetime,
    join_url: str,
    meeting_id: int,
    passcode: str | None,
    timezone_name: str,
) -> str:
    uid = f"{uuid.uuid4()}@agentmail"
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    vtimezone = """BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""

    dtstart = start_local.strftime("%Y%m%dT%H%M%S")
    dtend = end_local.strftime("%Y%m%dT%H%M%S")

    description_lines = [
        "Zoom meeting invite.",
        f"Join: {join_url}",
        f"Meeting ID: {meeting_id}",
    ]
    if passcode:
        description_lines.append(f"Passcode: {passcode}")
    description = "\\n".join(description_lines)

    attendees: list[str] = []
    for p in to_participants:
        cn = p.name or p.email
        attendees.append(
            f"ATTENDEE;CN={cn};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{p.email}"
        )
    for p in cc_participants:
        cn = p.name or p.email
        attendees.append(
            f"ATTENDEE;CN={cn};ROLE=OPT-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=FALSE:mailto:{p.email}"
        )

    ics = f"""BEGIN:VCALENDAR
PRODID:-//AgentMail//Zoom Calendar Invite//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:REQUEST
{vtimezone if timezone_name == "America/New_York" else ""}
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;TZID={timezone_name}:{dtstart}
DTEND;TZID={timezone_name}:{dtend}
SUMMARY:{topic}
DESCRIPTION:{description}
LOCATION:{join_url}
URL:{join_url}
ORGANIZER;CN={ics_quote_param_value(organizer_name)}:mailto:{organizer_email}
{chr(10).join(attendees)}
END:VEVENT
END:VCALENDAR
"""
    return ics


def send_agentmail_invite(
    *,
    inbox_id: str,
    api_key: str,
    to_emails: list[str],
    cc_emails: list[str],
    subject: str,
    ics: str,
    body_text: str,
    body_html: str,
    inbox_display_name: str | None = None,
) -> str:
    if AgentMail is None or SendAttachment is None:
        raise SystemExit(
            "agentmail is not installed in this Python environment. Try: .venv_agentmail/bin/python ..."
        )

    client = AgentMail(api_key=api_key)
    display_name = (inbox_display_name or "").strip()
    if display_name:
        client.inboxes.update(inbox_id, display_name=display_name)
    ics_b64 = base64.b64encode(ics.encode("utf-8")).decode("ascii")
    attachment = SendAttachment(
        filename="invite.ics",
        content_type="text/calendar; charset=utf-8; method=REQUEST",
        content_disposition="attachment",
        content=ics_b64,
    )

    resp = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=to_emails,
        cc=cc_emails or None,
        subject=subject,
        text=body_text,
        html=body_html,
        attachments=[attachment],
        headers={"Content-Class": "urn:content-classes:calendarmessage"},
    )
    return getattr(resp, "message_id", None) or getattr(resp, "messageId", None) or str(resp)


def render_markdown_to_text(markdown: str) -> str:
    lines: list[str] = []
    for raw in (markdown or "").splitlines():
        line = raw.rstrip()
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        if line.strip() == "──────────":
            lines.append("----------")
            continue
        # Minimal inline Markdown removal for our template.
        line = line.replace("**", "").replace("*", "")
        lines.append(line)
    return "\n".join(lines).rstrip("\n") + "\n"


def render_markdown_to_html(markdown: str) -> str:
    def render_inline(text: str) -> str:
        safe = html_escape(text)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
        # Italics: avoid matching the asterisks used for bold.
        safe = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", safe)
        return safe

    parts: list[str] = []
    for raw in (markdown or "").splitlines():
        line = raw.rstrip()
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        if line.strip() == "──────────":
            parts.append("<hr />")
            continue
        parts.append(render_inline(line))

    content = "<br/>\n".join(parts).rstrip()
    # Most email clients honor inline styles more reliably than <style> tags.
    return (
        '<div style="font-family: Georgia, serif; font-size: 12px; line-height: 1.4;">'
        f"{content}"
        "</div>"
    )


def build_zoom_style_body_text(
    *,
    topic: str,
    chat_topic: str | None,
    host_name: str,
    host_email: str,
    to_participants: list[Participant],
    cc_participants: list[Participant],
    start_local: datetime,
    end_local: datetime,
    timezone_name: str,
    join_url: str,
    meeting_id_pretty: str,
    passcode: str | None,
) -> str:
    template_path = Path(__file__).resolve().parent.parent / "references" / "body-template.md"
    template = template_path.read_text(encoding="utf-8")

    date_human = f"{start_local.strftime('%B')} {start_local.day}, {start_local.year}"
    time_start = start_local.strftime("%I:%M %p").lstrip("0")
    time_end = end_local.strftime("%I:%M %p").lstrip("0")
    tz_abbrev = start_local.strftime("%Z") or timezone_name
    when = f"{date_human} · {time_start} – {time_end} {tz_abbrev} ({timezone_name})"

    participants_emails = ", ".join([p.email for p in (to_participants + cc_participants)]) or ""
    effective_topic = (chat_topic or "").strip() or (topic or "Zoom Meeting")

    rendered = (
        template.replace("<Topic>", topic or "Zoom Meeting")
        .replace("<Chat topic>", effective_topic)
        .replace("<Host name>", host_name or "")
        .replace("<host email>", host_email or "")
        .replace("<Participants>", participants_emails)
        .replace("<When>", when)
        .replace("<Zoom join URL>", join_url)
        .replace("<Meeting ID>", meeting_id_pretty)
        .replace("<Passcode>", (passcode or "").strip())
    )

    # If optional fields are empty, remove their lines to avoid "Chat topic:" / empty passcode blocks.
    rendered_lines = rendered.splitlines()
    cleaned: list[str] = []
    i = 0
    while i < len(rendered_lines):
        line = rendered_lines[i]

        # Remove the Passcode block when empty: the "**Passcode**" line and the following value line.
        if (line.strip() == "**Passcode**") and (i + 1 < len(rendered_lines)) and (not rendered_lines[i + 1].strip()):
            i += 2
            continue

        cleaned.append(line.rstrip())
        i += 1

    return "\n".join(cleaned).rstrip("\n") + "\n"


def parse_args() -> argparse.Namespace:
    skill_dir = Path(__file__).resolve().parents[1]
    default_env_file = skill_dir / ".env.scheduler"
    legacy_env_file = skill_dir / ".env.zoom"
    if not default_env_file.exists() and legacy_env_file.exists():
        default_env_file = legacy_env_file
    p = argparse.ArgumentParser(description="Create a Zoom meeting via API and email a calendar invite via AgentMail.")
    p.add_argument(
        "--env-file",
        default=str(default_env_file),
        help="Optional .env-style file to source (only fills missing env vars). Default: ai-scheduler/.env.scheduler",
    )
    p.add_argument("--topic", default="Zoom Meeting", help="Meeting topic (used for Zoom title + email subject).")
    p.add_argument("--chat-topic", default=None, help="Optional: included in the email body as the meeting topic.")
    p.add_argument(
        "--host-name",
        default=None,
        help='Shown in the Participants line in the email body (default: env AGENTMAIL_HOST_NAME or AGENTMAIL_INBOX_DISPLAY_NAME or "Ryan Z. Nie").',
    )
    p.add_argument(
        "--subject-prefix",
        default=None,
        help="Optional subject prefix (default: env AGENTMAIL_SUBJECT_PREFIX).",
    )
    p.add_argument(
        "--no-subject-prefix",
        action="store_true",
        help="Do not use a subject prefix (ignores AGENTMAIL_SUBJECT_PREFIX / --subject-prefix).",
    )
    p.add_argument(
        "--subject-topic-only",
        action="store_true",
        help="Use a topic-only subject (no \"<TO_NAME>:\" prefix), regardless of recipient count.",
    )
    p.add_argument(
        "--to",
        dest="to_emails",
        action="append",
        default=[],
        help="Comma-separated list. Can be repeated.",
    )
    p.add_argument(
        "--cc",
        dest="cc_emails",
        action="append",
        default=[],
        help="Comma-separated list. Can be repeated.",
    )
    p.add_argument("--tz", dest="timezone_name", default="America/New_York")
    p.add_argument("--start", default=None, help='Local start like "YYYY-MM-DD HH:MM" (default: next 7:00 PM in --tz)')
    p.add_argument("--duration", type=int, default=30, help="Duration in minutes")
    p.add_argument("--agenda", default=None)
    p.add_argument("--existing-join-url", default=None, help="If set, skip Zoom API and use this join URL.")
    p.add_argument("--existing-meeting-id", type=int, default=None, help="If set (with --existing-join-url), skip Zoom API.")
    p.add_argument("--existing-passcode", default=None, help="Optional passcode to include when using existing meeting details.")
    p.add_argument(
        "--no-email",
        action="store_true",
        help="Only create the Zoom meeting; do not send a calendar invite email.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt before sending the email.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    to_raw = ",".join(args.to_emails or [])
    to_participants = parse_participants(to_raw)
    if not to_participants:
        raise SystemExit("At least one --to email is required.")
    cc_raw = ",".join(args.cc_emails or [])
    cc_participants = parse_participants(cc_raw)
    host_email_raw = (os.environ.get("AGENTMAIL_HOST") or "").strip()
    host_participants = parse_participants(host_email_raw)
    cc_participants = merge_participants(cc_participants, host_participants)

    if args.no_subject_prefix:
        subject_prefix = ""
    else:
        subject_prefix = (args.subject_prefix or os.environ.get("AGENTMAIL_SUBJECT_PREFIX") or "").strip()
        if not subject_prefix:
            raise SystemExit(
                "Missing subject prefix. Set AGENTMAIL_SUBJECT_PREFIX in ai-scheduler/.env.scheduler (or pass --subject-prefix), "
                "or pass --no-subject-prefix."
            )
    host_name = (
        (args.host_name or "").strip()
        or (os.environ.get("AGENTMAIL_HOST_NAME") or "").strip()
        or (os.environ.get("AGENTMAIL_INBOX_DISPLAY_NAME") or "").strip()
        or "Ryan Z. Nie"
    )
    topic = normalize_topic(args.topic, subject_prefix=subject_prefix)
    if args.subject_topic_only:
        subject = format_subject_topic_only(topic=topic, subject_prefix=subject_prefix)
    else:
        subject = format_subject(topic=topic, to_participants=to_participants, subject_prefix=subject_prefix)

    tz = ZoneInfo(args.timezone_name)
    if args.start:
        start_local = datetime.strptime(args.start, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    else:
        now_local = datetime.now(tz)
        candidate = now_local.replace(hour=19, minute=0, second=0, microsecond=0)
        if candidate <= now_local:
            candidate = candidate + timedelta(days=1)
        start_local = candidate
    end_local = start_local + timedelta(minutes=args.duration)

    using_existing = bool(args.existing_join_url and args.existing_meeting_id)
    if using_existing:
        meeting = ZoomMeeting(
            meeting_id=args.existing_meeting_id,
            join_url=args.existing_join_url,
            start_time=start_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            timezone=args.timezone_name,
            password=args.existing_passcode,
        )
    else:
        account_id = _get_env("ZOOM_ACCOUNT_ID")
        client_id = _get_env("ZOOM_CLIENT_ID")
        client_secret = _get_env("ZOOM_CLIENT_SECRET")

        token = zoom_access_token(account_id=account_id, client_id=client_id, client_secret=client_secret)
        zoom_topic = sanitize_zoom_topic(subject)
        meeting = create_zoom_meeting(
            token=token,
            topic=zoom_topic,
            start_dt=start_local,
            duration_minutes=args.duration,
            timezone_name=args.timezone_name,
            agenda=args.agenda,
        )

    print("Zoom meeting details:")
    print(" - topic:", subject)
    print(" - start_time:", meeting.start_time)
    print(" - timezone:", meeting.timezone)
    print(" - meeting_id:", meeting.meeting_id)
    print(" - join_url:", meeting.join_url)
    if meeting.password:
        print(" - passcode:", meeting.password)
    if using_existing:
        print(" - source: existing (no Zoom API call)")

    if args.no_email:
        return

    inbox_id = _get_env("AGENTMAIL_INBOX_ID")
    host_email = host_participants[0].email if host_participants else inbox_id

    print_confirmation_summary(
        from_email=inbox_id,
        to_participants=to_participants,
        cc_participants=cc_participants,
        start_local=start_local,
        end_local=end_local,
        timezone_name=args.timezone_name,
        subject=subject,
    )
    meeting_id_pretty = format_zoom_meeting_id(meeting.meeting_id)

    body_markdown = build_zoom_style_body_text(
        topic=topic,
        chat_topic=args.chat_topic,
        host_name=host_name,
        host_email=host_email,
        to_participants=to_participants,
        cc_participants=cc_participants,
        start_local=start_local,
        end_local=end_local,
        timezone_name=args.timezone_name,
        join_url=meeting.join_url,
        meeting_id_pretty=meeting_id_pretty,
        passcode=meeting.password,
    )
    text = render_markdown_to_text(body_markdown)
    html = render_markdown_to_html(body_markdown)

    print_email_preview(subject=subject, body_text=text)

    if not args.yes:
        confirm_or_exit()

    ics = build_ics(
        organizer_email=host_email,
        organizer_name=host_name,
        to_participants=to_participants,
        cc_participants=cc_participants,
        topic=subject,
        start_local=start_local,
        end_local=end_local,
        join_url=meeting.join_url,
        meeting_id=meeting.meeting_id,
        passcode=meeting.password,
        timezone_name=args.timezone_name,
    )

    agentmail_key = _get_env("AGENTMAIL_API_KEY")
    message_id = send_agentmail_invite(
        inbox_id=inbox_id,
        api_key=agentmail_key,
        to_emails=[p.email for p in to_participants],
        cc_emails=[p.email for p in cc_participants],
        subject=subject,
        ics=ics,
        body_text=text,
        body_html=html,
        inbox_display_name=(os.environ.get("AGENTMAIL_INBOX_DISPLAY_NAME") or None),
    )
    print("AgentMail invite sent:")
    print(" - from:", inbox_id)
    print(" - to:", [_format_participant(p) for p in to_participants])
    print(" - cc:", [_format_participant(p) for p in cc_participants])
    print(" - message_id:", message_id)


if __name__ == "__main__":
    main()
