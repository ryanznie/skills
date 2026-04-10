#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SCOPES = ["https://www.googleapis.com/auth/calendar"]
DT_FORMAT = "%Y-%m-%d %H:%M"
DEFAULT_ENV_PATH = Path(__file__).resolve().parents[1] / ".env.calendar"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--env-file", default=str(DEFAULT_ENV_PATH))
    bootstrap_args, _ = bootstrap.parse_known_args()
    load_env_file(Path(bootstrap_args.env_file).expanduser())

    parser = argparse.ArgumentParser(
        description="Create or update a Google Calendar event."
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH))
    parser.add_argument("--summary", required=True)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD HH:MM")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD HH:MM")
    parser.add_argument(
        "--tz",
        default=os.environ.get("GOOGLE_CALENDAR_TZ"),
        help="IANA timezone",
    )
    parser.add_argument("--description")
    parser.add_argument("--location")
    parser.add_argument(
        "--calendar-id",
        default=os.environ.get("GOOGLE_CALENDAR_ID", "primary"),
    )
    parser.add_argument("--event-id", help="If provided, update this event")
    parser.add_argument("--attendee", action="append", default=[])
    parser.add_argument("--add-meet", action="store_true")
    parser.add_argument(
        "--client-secret",
        default=os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET"),
    )
    parser.add_argument(
        "--token-path",
        default=str(
            Path(
                os.environ.get(
                    "GOOGLE_CALENDAR_TOKEN_PATH",
                    Path(__file__).resolve().parents[1] / "token.json",
                )
            )
        ),
    )
    args = parser.parse_args()
    missing = []
    if not args.tz:
        missing.append("--tz or GOOGLE_CALENDAR_TZ")
    if not args.client_secret:
        missing.append("--client-secret or GOOGLE_CALENDAR_CLIENT_SECRET")
    if missing:
        parser.error("Missing required settings: " + ", ".join(missing))
    return args


def parse_local_datetime(raw: str, tz_name: str) -> datetime:
    return datetime.strptime(raw, DT_FORMAT).replace(tzinfo=ZoneInfo(tz_name))


def load_credentials(client_secret: str, token_path: str):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise SystemExit(
            "Missing Google Calendar dependencies. Install "
            "'google-api-python-client google-auth-oauthlib google-auth-httplib2'."
        ) from exc

    creds = None
    token_file = Path(token_path)
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
        creds = flow.run_local_server(port=0)

    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def build_event_body(args: argparse.Namespace) -> dict[str, Any]:
    start_dt = parse_local_datetime(args.start, args.tz)
    end_dt = parse_local_datetime(args.end, args.tz)
    if end_dt <= start_dt:
        raise SystemExit("--end must be after --start")

    event: dict[str, Any] = {
        "summary": args.summary,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": args.tz},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": args.tz},
    }
    if args.description:
        event["description"] = args.description
    if args.location:
        event["location"] = args.location
    if args.attendee:
        event["attendees"] = [{"email": email} for email in args.attendee]
    return event


def main() -> int:
    args = parse_args()
    creds = load_credentials(args.client_secret, args.token_path)

    try:
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise SystemExit(
            "Missing google-api-python-client. Install required Google Calendar packages."
        ) from exc

    service = build("calendar", "v3", credentials=creds)
    event = build_event_body(args)

    conference_request_id = None
    if args.add_meet:
        conference_request_id = str(uuid.uuid4())
        event["conferenceData"] = {
            "createRequest": {
                "requestId": conference_request_id,
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    if args.event_id:
        request = service.events().update(
            calendarId=args.calendar_id,
            eventId=args.event_id,
            body=event,
            conferenceDataVersion=1 if args.add_meet else 0,
            sendUpdates="all" if args.attendee else "none",
        )
        result = request.execute()
        action = "updated"
    else:
        request = service.events().insert(
            calendarId=args.calendar_id,
            body=event,
            conferenceDataVersion=1 if args.add_meet else 0,
            sendUpdates="all" if args.attendee else "none",
        )
        result = request.execute()
        action = "created"

    output = {
        "action": action,
        "calendar_id": args.calendar_id,
        "event_id": result.get("id"),
        "html_link": result.get("htmlLink"),
        "status": result.get("status"),
    }
    if result.get("hangoutLink"):
        output["hangout_link"] = result["hangoutLink"]

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
