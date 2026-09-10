"""Habit tracking service."""

from datetime import datetime
from ..models import track_habit, show_habits


def track(habit: str | None = None, date: datetime | None = None) -> str | None:
    if not habit:
        return None
    return track_habit(habit, date)


def interactive_habit() -> str:
    from ..utils import dim, RESET, err
    print(f"{dim}Interactive habit log (press Ctrl+C to cancel){RESET}")
    habit = input("Habit: ").strip()
    if not habit:
        err("No habit entered.")
        raise SystemExit(1)
    return habit


def show() -> str:
    return show_habits()