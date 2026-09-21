import base64
import os
import argparse
import json
from html import escape
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agentmail import AgentMail
from agentmail.attachments.types.send_attachment import SendAttachment


parser = argparse.ArgumentParser(description="Send a calendar update using an existing iCalendar UID.")
parser.add_argument("--uid", required=True)
parser.add_argument("--to", required=True)
parser.add_argument("--cc", default="")
parser.add_argument("--host-email", default=None)
parser.add_argument("--host-name", default="Ryan Z. Nie")
parser.add_argument("--subject", required=True)
parser.add_argument("--topic", required=True)
parser.add_argument("--start", required=True, help="Local time: YYYY-MM-DD HH:MM")
parser.add_argument("--previous-start", default=None, help="Previous local start, shown struck through in the email body")
parser.add_argument("--duration", type=int, default=30)
parser.add_argument("--tz", default="America/New_York")
parser.add_argument("--location", required=True)
parser.add_argument("--sequence", type=int, default=1)
args = parser.parse_args()

skill_dir = Path(__file__).resolve().parents[1]
for line in (skill_dir / ".env.scheduler").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

host_email = args.host_email or os.environ.get("AGENTMAIL_HOST") or os.environ["AGENTMAIL_INBOX_ID"]

from zoneinfo import ZoneInfo

start_local = datetime.strptime(args.start, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(args.tz))
end_local = start_local + timedelta(minutes=args.duration)
uid = args.uid
dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
dtstart = start_local.strftime("%Y%m%dT%H%M%S")
dtend = end_local.strftime("%Y%m%dT%H%M%S")
ics = f'''BEGIN:VCALENDAR
PRODID:-//AgentMail//Calendar Update//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
SEQUENCE:{args.sequence}
DTSTAMP:{dtstamp}
DTSTART;TZID={args.tz}:{dtstart}
DTEND;TZID={args.tz}:{dtend}
SUMMARY:{args.subject}
DESCRIPTION:{args.topic}
LOCATION:{args.location}
ORGANIZER;CN="{args.host_name}":mailto:{host_email}
ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{args.to}
ATTENDEE;CN={args.host_name};ROLE=OPT-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=FALSE:mailto:{host_email}
END:VEVENT
END:VCALENDAR
'''

client = AgentMail(api_key=os.environ["AGENTMAIL_API_KEY"])
date_label = start_local.strftime("%A, %B %-d, %Y")
time_label = f"{start_local.strftime('%-I:%M %p')}–{end_local.strftime('%-I:%M %p %Z')}"
previous_time_label = None
if args.previous_start:
    previous_start = datetime.strptime(args.previous_start, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(args.tz))
    previous_end = previous_start + timedelta(minutes=args.duration)
    previous_time_label = f"{previous_start.strftime('%-I:%M %p')}–{previous_end.strftime('%-I:%M %p %Z')}"
when_text = f"{date_label} · {time_label}"
when_html = escape(when_text)
if previous_time_label:
    when_text = f"{date_label} · [Previous: {previous_time_label}] → {time_label}"
    when_html = f"{escape(date_label)} · <s>{escape(previous_time_label)}</s><br>{escape(time_label)}"
text_body = (
    "Disclaimer: This meeting invite was sent by an AI agent.\n\n"
    f"Topic: {args.topic}\n\n"
    f"Host\n{args.host_name} <{host_email}>\n\n"
    f"Participants\n{args.to}, {args.host_name}\n\n"
    f"When\n{when_text}\n\n"
    f"Location\n{args.location}"
)
html_body = f'''<p><em>Disclaimer: This meeting invite was sent by an AI agent.</em></p>
<p><strong>Topic</strong><br>{escape(args.topic)}</p>
<p><strong>Host</strong><br>{escape(args.host_name)} &lt;{escape(host_email)}&gt;</p>
<p><strong>Participants</strong><br>{escape(args.to)}, {escape(args.host_name)}</p>
<p><strong>When</strong><br>{when_html}</p>
<p><strong>Location</strong><br>{escape(args.location)}</p>'''
attachment = SendAttachment(
    filename="invite-update.ics",
    content_type="text/calendar; charset=utf-8; method=REQUEST",
    content_disposition="attachment",
    content=base64.b64encode(ics.encode()).decode(),
)
response = client.inboxes.messages.send(
    inbox_id=os.environ["AGENTMAIL_INBOX_ID"],
    to=[args.to],
    cc=[x.strip() for x in args.cc.split(",") if x.strip()] or None,
    subject=args.subject,
    text=text_body,
    html=html_body,
    attachments=[attachment],
    headers={"Content-Class": "urn:content-classes:calendarmessage"},
)
print("Calendar update sent:", getattr(response, "message_id", None) or getattr(response, "messageId", None) or response)
message_id = getattr(response, "message_id", None) or getattr(response, "messageId", None) or str(response)
event_log = skill_dir / ".event-log.jsonl"
with event_log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({
        "uid": uid,
        "sequence": args.sequence,
        "subject": args.subject,
        "to": [args.to],
        "cc": [x.strip() for x in args.cc.split(",") if x.strip()],
        "start": start_local.isoformat(),
        "end": end_local.isoformat(),
        "timezone": args.tz,
        "location": args.location,
        "message_id": message_id,
    }) + "\n")
