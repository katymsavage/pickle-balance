#!/usr/bin/env python3
"""Build the public schedule (schedule/schedule.json) from a raw Google Calendar export.

Usage:
    python3 scripts/build_schedule.py RAW_EVENTS.json [--today YYYY-MM-DD]

RAW_EVENTS.json is a JSON list of Google Calendar events (each with "summary",
"start" and "end"; optional "status" and "transparency"). It holds private details, so keep it
OUTSIDE this repository and never commit it.

Privacy rules (see scripts/schedule_config.json):
  * Events whose title matches a class rule are published with the class's
    public details from the config (never the event's description or guests).
  * Every other timed event is published only as an anonymous "Booked"
    time block: no title, no names.
  * All-day events and events marked "Free" (transparency: transparent)
    are dropped.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "schedule_config.json"
OUT = ROOT / "schedule" / "schedule.json"


def parse_dt(value, tz):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def classify(summary, cfg):
    s = " ".join(summary.lower().split())
    for rule in cfg["classes"]:
        if any(m in s for m in rule["match"]):
            return "class", rule
    for pat in cfg["booked_patterns"]:
        if re.search(pat, s):
            return "booked", None
    return None, None


def build(raw_events, cfg, today):
    tz = ZoneInfo(cfg["timezone"])
    horizon = today + timedelta(days=cfg["days_ahead"])
    out = []
    for ev in raw_events:
        if ev.get("status") == "cancelled":
            continue
        start, end = ev.get("start", {}), ev.get("end", {})
        if "dateTime" not in start or "dateTime" not in end:
            continue  # all-day events are always private
        kind, rule = classify(ev.get("summary", ""), cfg)
        if kind is None:
            # Any other timed event blocks her time: show it as an anonymous
            # "Booked" block, unless it is marked Free in Google Calendar.
            if ev.get("transparency") == "transparent":
                continue
            kind = "booked"
        s, e = parse_dt(start["dateTime"], tz), parse_dt(end["dateTime"], tz)
        if not (today <= s.date() <= horizon):
            continue
        item = {
            "date": s.date().isoformat(),
            "start": s.strftime("%H:%M"),
            "end": e.strftime("%H:%M"),
            "kind": kind,
        }
        if kind == "class":
            title = rule["title"]
            if rule.get("title_from_event"):
                # e.g. "Master Drives with Evan" -> theme "Drives"
                m = re.match(r"\s*master\s+(.+?)(?:\s+with\b.*)?$", ev["summary"], re.I)
                if m and m.group(1).strip().lower() not in ("class",):
                    title = f"{rule['title']}: {m.group(1).strip()}"
            item.update({k: rule.get(k) for k in ("coaches", "level", "price", "location", "blurb", "signup", "signup_label")})
            item["title"] = title
        out.append(item)
    out.sort(key=lambda x: (x["date"], x["start"]))
    return {
        "updated": datetime.now(tz).strftime("%Y-%m-%dT%H:%M"),
        "from": today.isoformat(),
        "to": horizon.isoformat(),
        "contact_phone": cfg["contact_phone"],
        "early_roster_note": cfg["early_roster_note"],
        "offerings": cfg["offerings"],
        "events": out,
    }


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cfg = json.loads(CONFIG.read_text())
    tz = ZoneInfo(cfg["timezone"])
    today = datetime.now(tz).date()
    if "--today" in args:
        today = date.fromisoformat(args[args.index("--today") + 1])
    raw = json.loads(Path(args[0]).read_text())
    if isinstance(raw, dict):
        raw = raw.get("events", [])
    data = build(raw, cfg, today)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    n_class = sum(e["kind"] == "class" for e in data["events"])
    n_booked = sum(e["kind"] == "booked" for e in data["events"])
    print(f"Wrote {OUT.relative_to(ROOT)}: {n_class} classes, {n_booked} booked blocks, "
          f"{len(raw) - n_class - n_booked} private events left out")


if __name__ == "__main__":
    main()
