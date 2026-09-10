"""Argument parser setup."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Personal AI Tracking Assistant — powered by OpenRouter",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize tracker folders and config")

    log_p = sub.add_parser("log", help="Log an activity")
    log_p.add_argument("activity", nargs="?", default=None, help="Activity description")
    log_p.add_argument("duration", nargs="?", type=int, default=None, help="Duration in minutes")
    log_p.add_argument("type", nargs="?", default="work", help="Activity type")
    log_p.add_argument("--notes", "-n", default="", help="Additional notes")

    goal_p = sub.add_parser("goal", help="Add a goal to today")
    goal_p.add_argument("text", help="Goal text")

    done_p = sub.add_parser("done", help="Mark a goal complete")
    done_p.add_argument("text", help="Goal text (must match exactly)")

    sub.add_parser("today", help="Show today's log")
    sub.add_parser("yesterday", help="Show yesterday's log")

    week_p = sub.add_parser("week", help="Generate weekly report with AI analysis")
    week_p.add_argument("--no-stream", action="store_true", help="Don't stream")

    month_p = sub.add_parser("month", help="Generate monthly summary with AI analysis")
    month_p.add_argument("--no-stream", action="store_true", help="Don't stream")

    proj_p = sub.add_parser("project", help="Open/create project")
    proj_p.add_argument("name", help="Project name")

    habit_p = sub.add_parser("habit", help="Track a habit")
    habit_p.add_argument("name", nargs="?", default=None, help="Habit description")
    habit_p.add_argument("--show", action="store_true", help="Show all habits")

    review_p = sub.add_parser("review", help="Get AI's daily review/roast")
    review_p.add_argument("--no-stream", action="store_true", help="Don't stream")

    sleep_p = sub.add_parser("sleep", help="Log bedtime or wake time")
    sleep_p.add_argument("--bedtime", default=None, help="Bedtime HH:MM")
    sleep_p.add_argument("--wakeup", default=None, help="Wake time HH:MM")
    sleep_p.add_argument("--notes", "-n", default="", help="Notes")

    special_p = sub.add_parser("special", help="Set day context (exam/college/holiday/normal)")
    special_p.add_argument("day_type", nargs="?", default=None, help="Day type")
    special_p.add_argument("--notes", "-n", default="", help="Notes")

    sub.add_parser("stats", help="Show stats: hours, trends, streaks")

    search_p = sub.add_parser("search", help="Search all logs for keyword")
    search_p.add_argument("keyword", help="Search keyword")

    export_p = sub.add_parser("export", help="Export data")
    export_p.add_argument("format", nargs="?", default="json", help="Export format (json)")

    sub.add_parser("report", help="Generate comprehensive report")

    return parser