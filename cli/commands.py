"""CLI command implementations."""

import argparse
from ..services import (
    TrackerService,
    log_activity,
    interactive_log,
    add_goal,
    complete_goal,
    log_sleep,
    interactive_sleep,
    set_day_context,
    interactive_day_context,
    track_habit,
    interactive_habit,
    show_habits,
    weekly,
    monthly,
    all_stats,
)
from ..cli.formatters import format_review, format_weekly, format_monthly
from ..utils import err, ok


def cmd_init(args: argparse.Namespace) -> None:
    TrackerService().init()


def cmd_log(args: argparse.Namespace) -> None:
    service = TrackerService()
    activity = getattr(args, "activity", None)
    start = getattr(args, "start", None)
    end = getattr(args, "end", None)
    act_type = getattr(args, "type", "work") or "work"
    notes = getattr(args, "notes", "") or ""

    # Detect legacy usage: `tracker log "Study" 30 work` → start=duration, end=type
    # Also handle `tracker log "Study" 30` → start=duration, end=None
    from ..utils.time_utils import parse_time
    from ..models.daily_log import TYPES

    is_legacy = False
    if activity and start:
        start_str = str(start).strip()
        if start_str.isdigit():
            if end is None:
                is_legacy = True
            elif isinstance(end, str) and (end in TYPES or not parse_time(end)):
                is_legacy = True

    def _handle_msg(msg: str | None) -> None:
        if not msg:
            ok("Done")
            return
        if msg.startswith("Invalid"):
            err(msg)
        else:
            ok(msg)

    if is_legacy:
        # Legacy: start is duration, end is type (or None), act_type holds default or notes
        # Re-map: duration=start, type=end
        legacy_duration = start
        legacy_type = end if isinstance(end, str) and end in TYPES else act_type if act_type in TYPES else "work"
        msg = log_activity(activity, legacy_duration, legacy_type, notes=notes)
        # log_activity shim will handle computing start/end
        if msg:
            _handle_msg(msg)
            return

    if activity and start and end:
        # Check that start/end are valid times before calling; if not, treat as legacy or error
        if parse_time(str(start)) and parse_time(str(end)):
            msg = log_activity(activity, start, end, act_type, notes)
            _handle_msg(msg)
            return
        # If times invalid but we have a legacy-like duration, try legacy handling
        if str(start).strip().isdigit():
            msg = log_activity(activity, start, end, act_type, notes)
            if msg:
                _handle_msg(msg)
                return
        # Invalid times → show error
        err(f"Invalid time format. Use HH:MM (e.g. 09:00). Got start='{start}' end='{end}'")
        return
    else:
        activity, start, end, act_type, notes = interactive_log()
        msg = log_activity(activity, start, end, act_type, notes)
        _handle_msg(msg)


def cmd_goal(args: argparse.Namespace) -> None:
    ok(add_goal(args.text))


def cmd_done(args: argparse.Namespace) -> None:
    ok(complete_goal(args.text))


def cmd_today(args: argparse.Namespace) -> None:
    from ..models import display
    print(display())


def cmd_yesterday(args: argparse.Namespace) -> None:
    from ..models import display
    from datetime import datetime, timedelta
    print(display(datetime.now() - timedelta(days=1)))


def cmd_week(args: argparse.Namespace) -> None:
    service = TrackerService()
    format_weekly(service, not getattr(args, "no_stream", False))


def cmd_month(args: argparse.Namespace) -> None:
    service = TrackerService()
    format_monthly(service, not getattr(args, "no_stream", False))


def cmd_project(args: argparse.Namespace) -> None:
    from ..models import open_project
    print(open_project(args.name))


def cmd_habit(args: argparse.Namespace) -> None:
    if getattr(args, "show", False):
        print(show_habits())
    elif args.name:
        ok(track_habit(args.name))
    else:
        err("Provide a habit name or use --show")


def cmd_review(args: argparse.Namespace) -> None:
    service = TrackerService()
    format_review(service, not getattr(args, "no_stream", False))


def cmd_sleep(args: argparse.Namespace) -> None:
    bedtime = getattr(args, "bedtime", None)
    wakeup = getattr(args, "wakeup", None)
    notes = getattr(args, "notes", "") or ""

    if not bedtime and not wakeup:
        bedtime, wakeup, notes = interactive_sleep()

    msg = log_sleep(bedtime, wakeup, notes)
    if msg:
        ok(msg)


def cmd_special(args: argparse.Namespace) -> None:
    day_type = getattr(args, "day_type", None)
    notes = getattr(args, "notes", "") or ""

    if not day_type:
        day_type, notes = interactive_day_context()

    if day_type:
        ok(set_day_context(day_type, notes))


def cmd_stats(args: argparse.Namespace) -> None:
    print(all_stats())


def cmd_search(args: argparse.Namespace) -> None:
    from ..services import search
    print(search(args.keyword))


def cmd_export(args: argparse.Namespace) -> None:
    from ..services import export
    print(export(args.format))


def cmd_report(args: argparse.Namespace) -> None:
    TrackerService().report()