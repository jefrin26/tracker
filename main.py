"""Main entry point."""

from .cli import build_parser
from .cli.commands import (
    cmd_done,
    cmd_export,
    cmd_goal,
    cmd_habit,
    cmd_init,
    cmd_log,
    cmd_month,
    cmd_project,
    cmd_report,
    cmd_review,
    cmd_search,
    cmd_sleep,
    cmd_special,
    cmd_stats,
    cmd_today,
    cmd_week,
    cmd_yesterday,
)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "log": cmd_log,
        "goal": cmd_goal,
        "done": cmd_done,
        "today": cmd_today,
        "yesterday": cmd_yesterday,
        "week": cmd_week,
        "month": cmd_month,
        "project": cmd_project,
        "habit": cmd_habit,
        "review": cmd_review,
        "sleep": cmd_sleep,
        "special": cmd_special,
        "stats": cmd_stats,
        "search": cmd_search,
        "export": cmd_export,
        "report": cmd_report,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()