"""Log activity service."""

from datetime import datetime
from ..models import TYPES, add_activity


def log_activity(
    activity: str | None,
    duration: int | None,
    act_type: str = "work",
    notes: str = "",
    date: datetime | None = None,
) -> str | None:
    """Log an activity. Returns message or None if interactive."""
    if activity and duration:
        return add_activity(activity, duration, act_type, notes=notes, date=date)
    return None


def interactive_log() -> tuple[str, int, str, str]:
    """Run interactive log prompts. Returns (activity, duration, type, notes)."""
    from ..utils import dim, err, RESET
    print(f"{dim}Interactive log (press Ctrl+C to cancel){RESET}")
    activity = input("Activity: ").strip()
    if not activity:
        err("No activity entered.")
        raise SystemExit(1)
    dur_str = input("Duration (minutes): ").strip()
    if not dur_str.isdigit():
        err("Duration must be a number.")
        raise SystemExit(1)
    duration = int(dur_str)
    act_type = input(f"Type ({'/'.join(TYPES)}): ").strip() or "work"
    notes = input("Notes (optional): ").strip()
    return activity, duration, act_type, notes