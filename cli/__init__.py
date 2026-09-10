"""CLI package."""

from .commands import (
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
from .parser import build_parser

__all__ = [
    "build_parser",
    "cmd_done",
    "cmd_export",
    "cmd_goal",
    "cmd_habit",
    "cmd_init",
    "cmd_log",
    "cmd_month",
    "cmd_project",
    "cmd_report",
    "cmd_review",
    "cmd_search",
    "cmd_sleep",
    "cmd_special",
    "cmd_stats",
    "cmd_today",
    "cmd_week",
    "cmd_yesterday",
]