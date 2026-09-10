"""Sleep tracking service."""

from datetime import datetime
from ..models import log_bedtime, log_wakeup, get_sleep


def log_sleep(
    bedtime: str | None = None,
    wakeup: str | None = None,
    notes: str = "",
    date: datetime | None = None,
) -> str | None:
    """Log bedtime and/or wakeup. Returns message."""
    if not bedtime and not wakeup:
        return None
    msgs = []
    if bedtime:
        msgs.append(log_bedtime(bedtime, notes, date))
    if wakeup:
        msgs.append(log_wakeup(wakeup, notes, date))
    return "\n".join(msgs)


def interactive_sleep() -> tuple[str | None, str | None, str]:
    """Run interactive sleep prompts. Returns (bedtime, wakeup, notes)."""
    from ..utils import dim, RESET
    print(f"{dim}Interactive sleep log (press Ctrl+C to cancel){RESET}")
    bedtime = input("Bedtime (HH:MM): ").strip() or None
    wakeup = input("Wake time (HH:MM): ").strip() or None
    notes = input("Notes (optional): ").strip()
    return bedtime, wakeup, notes


def get_sleep_info(date: datetime | None = None) -> dict:
    return get_sleep(date)