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
    duration = getattr(args, "duration", None)
    act_type = getattr(args, "type", "work") or "work"
    notes = getattr(args, "notes", "") or ""

    if activity and duration:
        msg = log_activity(activity, duration, act_type, notes)
        ok(msg or "Done")
    else:
        activity, duration, act_type, notes = interactive_log()
        msg = log_activity(activity, duration, act_type, notes)
        ok(msg or "Done")


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