"""Day context (special days) domain model."""

import json
from datetime import datetime
from typing import Any

from ..storage import day_context_path, read_json, write_json


VALID_TYPES = {"exam", "college", "holiday", "normal"}


def set_context(day_type: str, notes: str = "", date: datetime | None = None) -> str:
    """Set the context for a day: exam, college, holiday, normal."""
    day_type = day_type.strip().lower()
    if day_type not in VALID_TYPES:
        return f"Invalid day type. Use one of: {', '.join(sorted(VALID_TYPES))}"
    d = date or datetime.now()
    data = {"day_type": day_type, "notes": notes.strip()}
    write_json(day_context_path(d), data)
    return f"Day context set: {day_type}"


def get_context(date: datetime | None = None) -> dict[str, str]:
    """Get day context."""
    d = date or datetime.now()
    data = read_json(day_context_path(d))
    return {
        "day_type": data.get("day_type", "normal"),
        "notes": data.get("notes", ""),
    }