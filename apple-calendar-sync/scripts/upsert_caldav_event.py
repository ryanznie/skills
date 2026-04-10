#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

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
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_args() -> argparse.Namespace:
    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--env-file", default=str(DEFAULT_ENV_PATH))
    bootstrap_args, _ = bootstrap.parse_known_args()
    load_env_file(Path(bootstrap_args.env_file).expanduser())

    parser = argparse.ArgumentParser(
        description="Create or update a CalDAV event, including iCloud Calendar."
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH))
    parser.add_argument("--summary")
    parser.add_argument("--start", help="YYYY-MM-DD HH:MM")
    parser.add_argument("--end", help="YYYY-MM-DD HH:MM")
    parser.add_argument(
        "--tz",
        default=os.environ.get("APPLE_CALENDAR_TZ"),
        help="IANA timezone",
    )
    parser.add_argument("--description")
    parser.add_argument("--location")
    parser.add_argument("--url")
    parser.add_argument("--uid", help="If provided, update the event with this UID")
    parser.add_argument(
        "--caldav-url",
        default=os.environ.get("APPLE_CALENDAR_CALDAV_URL", "https://caldav.icloud.com"),
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("APPLE_CALENDAR_USERNAME"),
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("APPLE_CALENDAR_PASSWORD"),
    )
    parser.add_argument(
        "--calendar-name",
        default=os.environ.get("APPLE_CALENDAR_NAME"),
    )
    parser.add_argument("--list-calendars", action="store_true")
    parser.add_argument("--create-calendar", help="Create a new calendar with this display name")
    args = parser.parse_args()
    missing = []
    if not args.tz:
        missing.append("--tz or APPLE_CALENDAR_TZ")
    if not args.caldav_url:
        missing.append("--caldav-url or APPLE_CALENDAR_CALDAV_URL")
    if not args.username:
        missing.append("--username or APPLE_CALENDAR_USERNAME")
    if not args.password:
        missing.append("--password or APPLE_CALENDAR_PASSWORD")
    if missing:
        parser.error("Missing required settings: " + ", ".join(missing))
    if not args.list_calendars and not args.create_calendar:
        event_missing = []
        if not args.summary:
            event_missing.append("--summary")
        if not args.start:
            event_missing.append("--start")
        if not args.end:
            event_missing.append("--end")
        if event_missing:
            parser.error("Missing required event fields: " + ", ".join(event_missing))
    return args


def parse_local_datetime(raw: str, tz_name: str) -> datetime:
    return datetime.strptime(raw, DT_FORMAT).replace(tzinfo=ZoneInfo(tz_name))


def build_icalendar_payload(args: argparse.Namespace) -> tuple[str, str]:
    try:
        from icalendar import Calendar, Event
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency. Install 'caldav' and 'icalendar' first."
        ) from exc

    start_dt = parse_local_datetime(args.start, args.tz)
    end_dt = parse_local_datetime(args.end, args.tz)
    if end_dt <= start_dt:
        raise SystemExit("--end must be after --start")

    uid = args.uid or f"{uuid.uuid4()}@local.agent"

    cal = Calendar()
    cal.add("prodid", "-//Codex Skills//Apple Calendar Sync//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("uid", uid)
    event.add("summary", args.summary)
    event.add("dtstamp", datetime.now(UTC))
    event.add("dtstart", start_dt)
    event.add("dtend", end_dt)
    if args.description:
        event.add("description", args.description)
    if args.location:
        event.add("location", args.location)
    if args.url:
        event.add("url", args.url)

    cal.add_component(event)
    return uid, cal.to_ical().decode("utf-8")


def choose_calendar(principal, calendar_name: str | None):
    calendars = principal.calendars()
    if not calendars:
        raise SystemExit("No calendars found for this CalDAV account.")

    if calendar_name:
        for cal in calendars:
            display_name = getattr(cal, "name", None) or cal.get_display_name()
            if display_name == calendar_name:
                return cal
        names = ", ".join((getattr(cal, "name", None) or cal.get_display_name()) for cal in calendars)
        raise SystemExit(
            f"Calendar {calendar_name!r} not found. Available calendars: {names}"
        )

    if len(calendars) == 1:
        return calendars[0]

    names = ", ".join((getattr(cal, "name", None) or cal.get_display_name()) for cal in calendars)
    raise SystemExit(
        f"Multiple calendars found. Re-run with --calendar-name. Available calendars: {names}"
    )


def list_calendars(principal) -> list[str]:
    return [(getattr(cal, "name", None) or cal.get_display_name()) for cal in principal.calendars()]


def find_event_by_uid(calendar, uid: str):
    try:
        results = calendar.search(comp_class="VEVENT")
    except TypeError:
        results = calendar.events()
    for event in results:
        data = event.data
        if f"UID:{uid}" in data or f"UID:{uid}\r\n" in data:
            return event
    return None


def main() -> int:
    args = parse_args()

    try:
        import caldav
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency. Install 'caldav' and 'icalendar' first."
        ) from exc

    client = caldav.DAVClient(
        url=args.caldav_url,
        username=args.username,
        password=args.password,
    )
    principal = client.principal()

    if args.list_calendars:
        print(json.dumps({"calendars": list_calendars(principal)}, indent=2))
        return 0

    if args.create_calendar:
        calendar = principal.make_calendar(name=args.create_calendar)
        calendar_name = getattr(calendar, "name", None) or calendar.get_display_name()
        print(
            json.dumps(
                {
                    "action": "calendar_created",
                    "calendar_name": calendar_name,
                },
                indent=2,
            )
        )
        return 0

    calendar = choose_calendar(principal, args.calendar_name)
    uid, ical = build_icalendar_payload(args)

    existing = find_event_by_uid(calendar, uid) if args.uid else None
    if existing:
        existing.data = ical
        existing.save()
        action = "updated"
    else:
        calendar.save_event(ical)
        action = "created"

    print(
        json.dumps(
            {
                "action": action,
                "calendar_name": getattr(calendar, "name", None) or calendar.get_display_name(),
                "uid": uid,
                "start": args.start,
                "end": args.end,
                "timezone": args.tz,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        raise SystemExit(130)
