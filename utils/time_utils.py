"""Time parsing and formatting utilities."""

import re
from datetime import datetime, timedelta
from typing import Optional


TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def parse_time(time_str: str) -> Optional[tuple[int, int]]:
    """Parse HH:MM or H:MM into (hour, minute). Returns None on failure."""
    time_str = time_str.strip()
    m = TIME_RE.match(time_str)
    if not m:
        return None
    hh, mm = int(m.group(1)), int(m.group(2))
    if hh > 23 or mm > 59:
        return None
    return hh, mm


def to_minutes(hh: int, mm: int) -> int:
    """Convert hour/minute to total minutes."""
    return hh * 60 + mm


def to_hhmm(minutes: int) -> str:
    """Convert minutes to HH:MM string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def uptime_minutes(bedtime: str, wake_time: str) -> Optional[int]:
    """Compute minutes between bedtime and wake time (handles overnight)."""
    b = parse_time(bedtime)
    w = parse_time(wake_time)
    if not b or not w:
        return None
    bed_m = to_minutes(*b)
    wake_m = to_minutes(*w)
    if wake_m <= bed_m:
        wake_m += 24 * 60
    return wake_m - bed_m


def duration_between(start: str, end: str) -> Optional[int]:
    """Calculate minutes between start and end times (handles overnight).

    Returns None if either time is invalid, or if duration is 0.
    If end < start, treats end as next day (overnight session).
    If end == start, returns None (zero duration).
    """
    s = parse_time(start)
    e = parse_time(end)
    if not s or not e:
        return None
    start_m = to_minutes(*s)
    end_m = to_minutes(*e)
    if end_m == start_m:
        return None
    if end_m < start_m:
        end_m += 24 * 60
    diff = end_m - start_m
    if diff <= 0:
        return None
    return diff


def format_uptime(minutes: Optional[int]) -> str:
    """Format minutes as 'X.Xh' or '—'."""
    if minutes is None:
        return "—"
    return f"{minutes / 60:.1f}h"


def now_hhmm() -> str:
    """Current time as HH:MM."""
    return datetime.now().strftime("%H:%M")


def today_str() -> str:
    """Today as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def yesterday_str() -> str:
    """Yesterday as YYYY-MM-DD."""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")