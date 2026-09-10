"""Log activity service."""

from datetime import datetime
from ..models import TYPES, add_activity


def log_activity(
    activity: str | None,
    start: str | int | None,
    end: str | None,
    act_type: str = "work",
    notes: str = "",
    date: datetime | None = None,
) -> str | None:
    """Log an activity using start/end times. Returns message or None if interactive.

    Backward-compatible: if `start` is a duration (int/digit) and `end` is a type,
    handles legacy `log_activity(activity, duration, type)`.
    """
    from ..utils.time_utils import parse_time

    if activity and start and end:
        # Detect legacy: start is duration, end is type (not a time)
        if isinstance(start, int) or (isinstance(start, str) and start.strip().isdigit()):
            if isinstance(end, str) and (end in TYPES or not parse_time(end)):
                # Legacy call: duration + type
                # act_type param actually holds notes or time in legacy, but we handle via add_activity shim
                return add_activity(activity, start, end, act_type, notes=notes, date=date)  # type: ignore
        return add_activity(activity, start, end, act_type, notes=notes, date=date)  # type: ignore
    # Handle legacy 2-arg case: activity + duration without end (type default)
    if activity and start and not end:
        if isinstance(start, int) or (isinstance(start, str) and str(start).strip().isdigit()):
            # Treat as legacy duration with default type
            return add_activity(activity, start, act_type, notes=notes, date=date)  # type: ignore
    return None


def interactive_log() -> tuple[str, str, str, str, str]:
    """Run interactive log prompts. Returns (activity, start, end, type, notes)."""
    from ..utils import dim, err, parse_time, duration_between, RESET

    print(f"{dim}Interactive log (press Ctrl+C to cancel){RESET}")
    activity = input("Activity: ").strip()
    if not activity:
        err("No activity entered.")
        raise SystemExit(1)
    start = input("Start time (HH:MM, e.g. 09:00): ").strip()
    if not parse_time(start):
        err("Invalid start time. Use HH:MM (e.g. 09:00).")
        raise SystemExit(1)
    end = input("End time (HH:MM, e.g. 10:30): ").strip()
    if not parse_time(end):
        err("Invalid end time. Use HH:MM (e.g. 10:30).")
        raise SystemExit(1)
    dur = duration_between(start, end)
    if dur is None:
        err(f"Invalid time range: {start} → {end}. End must be after start.")
        raise SystemExit(1)
    print(f"  → Duration: {dur}m")
    act_type = input(f"Type ({'/'.join(TYPES)}): ").strip() or "work"
    notes = input("Notes (optional): ").strip()
    return activity, start, end, act_type, notes