#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import sys
import textwrap
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DISCLAIMER = "Disclaimer: This email was sent by an AI agent."
DT_FORMAT = "%Y-%m-%d %H:%M"


def _escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def _fold_ics_line(line: str, limit: int = 75) -> str:
    chunks = []
    while len(line.encode("utf-8")) > limit:
        split_at = min(len(line), limit)
        while len(line[:split_at].encode("utf-8")) > limit:
            split_at -= 1
        chunks.append(line[:split_at])
        line = " " + line[split_at:]
    chunks.append(line)
    return "\r\n".join(chunks)


def _format_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _parse_local_dt(raw: str, tz_name: str) -> datetime:
    return datetime.strptime(raw, DT_FORMAT).replace(tzinfo=ZoneInfo(tz_name))


@dataclass(frozen=True)
class Attendee:
    email: str
    common_name: str | None = None
    role: str = "REQ-PARTICIPANT"
    partstat: str = "NEEDS-ACTION"


def _parse_attendee(raw: str) -> Attendee:
    parts = [part.strip() for part in raw.split("|")]
    if not parts or not parts[0]:
        raise ValueError(f"Invalid attendee value: {raw!r}")
    email = parts[0]
    common_name = parts[1] if len(parts) > 1 and parts[1] else None
    role = parts[2] if len(parts) > 2 and parts[2] else "REQ-PARTICIPANT"
    return Attendee(email=email, common_name=common_name, role=role)


def build_ics(
    *,
    summary: str,
    start_dt: datetime,
    end_dt: datetime,
    organizer_email: str | None,
    organizer_name: str | None,
    attendees: list[Attendee],
    description: str | None,
    location: str | None,
    url: str | None,
    reminder_minutes: int | None,
) -> str:
    uid = f"{uuid.uuid4()}@local.agent"
    now_utc = datetime.now(UTC)
    lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//Codex Skills//ICS Sync//EN",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{_format_utc(now_utc)}",
        f"DTSTART:{_format_utc(start_dt)}",
        f"DTEND:{_format_utc(end_dt)}",
        f"SUMMARY:{_escape_ics(summary)}",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "TRANSP:OPAQUE",
    ]
    if description:
        lines.append(f"DESCRIPTION:{_escape_ics(description)}")
    if location:
        lines.append(f"LOCATION:{_escape_ics(location)}")
    if url:
        lines.append(f"URL:{_escape_ics(url)}")
    if organizer_email:
        if organizer_name:
            lines.append(
                f"ORGANIZER;CN={_escape_ics(organizer_name)}:mailto:{organizer_email}"
            )
        else:
            lines.append(f"ORGANIZER:mailto:{organizer_email}")
    for attendee in attendees:
        prefix = "ATTENDEE"
        params = [f"ROLE={attendee.role}", f"PARTSTAT={attendee.partstat}", "RSVP=TRUE"]
        if attendee.common_name:
            params.insert(0, f"CN={_escape_ics(attendee.common_name)}")
        lines.append(f"{prefix};{';'.join(params)}:mailto:{attendee.email}")
    if reminder_minutes is not None:
        lines.extend(
            [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:{_escape_ics(summary)}",
                f"TRIGGER:-PT{reminder_minutes}M",
                "END:VALARM",
            ]
        )
    lines.extend(["END:VEVENT", "END:VCALENDAR"])
    return "".join(f"{_fold_ics_line(line)}\r\n" for line in lines)


def _build_email_body(
    summary: str,
    start_dt: datetime,
    end_dt: datetime,
    tz_name: str,
    description: str | None,
    location: str | None,
    url: str | None,
) -> str:
    local_start = start_dt.astimezone(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M")
    local_end = end_dt.astimezone(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M")
    body = [
        DISCLAIMER,
        "",
        f"Event: {summary}",
        f"When: {local_start} to {local_end} ({tz_name})",
    ]
    if location:
        body.append(f"Location: {location}")
    if url:
        body.append(f"URL: {url}")
    if description:
        body.extend(["", description])
    body.extend(["", "Calendar invite attached as .ics."])
    return "\n".join(body)


def _send_via_agentmail(
    *,
    api_key: str,
    from_inbox: str,
    to: list[str],
    cc: list[str],
    subject: str,
    text_body: str,
    ics_content: str,
    filename: str,
) -> None:
    try:
        from agentmail import AgentMail
    except ImportError as exc:
        raise SystemExit(
            "AgentMail delivery requested but the 'agentmail' package is not installed."
        ) from exc

    client = AgentMail(api_key=api_key)
    attachment = {
        "content": base64.b64encode(ics_content.encode("utf-8")).decode("ascii"),
        "filename": filename,
        "content_type": "text/calendar; charset=utf-8; method=REQUEST",
    }
    client.inboxes.messages.send(
        inbox_id=from_inbox,
        to=to,
        cc=cc or None,
        subject=subject,
        text=text_body,
        html="<p><em>Disclaimer: This email was sent by an AI agent.</em></p>"
        + "".join(f"<p>{line}</p>" for line in text_body.splitlines()[2:] if line),
        attachments=[attachment],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an .ics invite and optionally send it via AgentMail."
    )
    parser.add_argument("--summary", required=True)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD HH:MM")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD HH:MM")
    parser.add_argument("--tz", required=True, help="IANA timezone, e.g. America/New_York")
    parser.add_argument("--description")
    parser.add_argument("--location")
    parser.add_argument("--url")
    parser.add_argument("--organizer-email")
    parser.add_argument("--organizer-name")
    parser.add_argument(
        "--attendee",
        action="append",
        default=[],
        help="email[|Common Name][|ROLE], repeat for multiple attendees",
    )
    parser.add_argument("--reminder-minutes", type=int)
    parser.add_argument("--output", default="/tmp/invite.ics")
    parser.add_argument("--subject")
    parser.add_argument("--body")
    parser.add_argument("--agentmail-api-key")
    parser.add_argument("--from-inbox")
    parser.add_argument("--to", action="append", default=[])
    parser.add_argument("--cc", action="append", default=[])
    parser.add_argument("--yes", action="store_true", help="Send without interactive confirmation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_dt = _parse_local_dt(args.start, args.tz)
    end_dt = _parse_local_dt(args.end, args.tz)
    if end_dt <= start_dt:
        raise SystemExit("--end must be after --start")

    attendees = [_parse_attendee(raw) for raw in args.attendee]
    ics_content = build_ics(
        summary=args.summary,
        start_dt=start_dt,
        end_dt=end_dt,
        organizer_email=args.organizer_email or args.from_inbox,
        organizer_name=args.organizer_name,
        attendees=attendees,
        description=args.description,
        location=args.location,
        url=args.url,
        reminder_minutes=args.reminder_minutes,
    )

    output_path = Path(args.output)
    output_path.write_text(ics_content, encoding="utf-8")

    print(f"Wrote .ics file: {output_path}")
    print(f"Event: {args.summary}")
    print(f"When: {args.start} to {args.end} ({args.tz})")

    if not args.to:
        return 0

    if not args.agentmail_api_key or not args.from_inbox:
        raise SystemExit(
            "--agentmail-api-key and --from-inbox are required when using --to"
        )

    subject = args.subject or f"Calendar Invite: {args.summary}"
    body = args.body or _build_email_body(
        args.summary, start_dt, end_dt, args.tz, args.description, args.location, args.url
    )

    preview = textwrap.dedent(
        f"""\
        From: {args.from_inbox}
        To: {", ".join(args.to)}
        CC: {", ".join(args.cc) if args.cc else "(none)"}
        Subject: {subject}

        {body}
        """
    )
    print("\nEmail preview\n")
    print(preview)

    if not args.yes:
        confirm = input("Send email? [y/N] ").strip().lower()
        if confirm not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    _send_via_agentmail(
        api_key=args.agentmail_api_key,
        from_inbox=args.from_inbox,
        to=args.to,
        cc=args.cc,
        subject=subject,
        text_body=body,
        ics_content=ics_content,
        filename=output_path.name,
    )
    print("Invite sent.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
