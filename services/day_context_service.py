"""Special day context service."""

from datetime import datetime
from ..models import VALID_TYPES, set_context, get_context


def set_day_context(
    day_type: str | None = None,
    notes: str = "",
    date: datetime | None = None,
) -> str | None:
    """Set day context. Returns message."""
    if not day_type:
        return None
    return set_context(day_type, notes, date)


def interactive_day_context() -> tuple[str | None, str]:
    """Run interactive day context prompts. Returns (day_type, notes)."""
    from ..utils import dim, RESET
    print(f"{dim}Interactive special day setup (press Ctrl+C to cancel){RESET}")
    day_type = input("Day type (exam / college / holiday / normal): ").strip() or None
    notes = input("Notes (optional): ").strip()
    return day_type, notes


def get_day_context(date: datetime | None = None) -> dict:
    return get_context(date)