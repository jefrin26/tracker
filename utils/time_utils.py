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


def get_day_phase(hour: int) -> str:
    """Return human day phase for hour (0-23)."""
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def day_progress_info(
    now: datetime | None = None, wake_str: str = "07:00", sleep_str: str = "23:00"
) -> dict:
    """Calculate day progress relative to wake→sleep window and midnight.

    Returns dict with: phase, elapsed_h, remaining_h, pct_wake,
    pct_midnight, gap info helper.
    """
    n = now or datetime.now()
    hh, mm = n.hour, n.minute
    cur_m = hh * 60 + mm

    wake = parse_time(wake_str) or (7, 0)
    sleep = parse_time(sleep_str) or (23, 0)
    wake_m = to_minutes(*wake)
    sleep_m = to_minutes(*sleep)
    # Handle overnight sleep window (e.g., sleep 01:00)
    if sleep_m <= wake_m:
        sleep_m += 24 * 60
        if cur_m < wake_m:
            cur_m += 24 * 60

    total_wake = sleep_m - wake_m
    elapsed_wake = max(0, min(cur_m - wake_m, total_wake))
    remaining_wake = max(0, total_wake - elapsed_wake)
    pct_wake = (elapsed_wake / total_wake * 100) if total_wake else 0

    # Midnight progress (0-24h)
    cur_mid_m = hh * 60 + mm
    pct_mid = cur_mid_m / (24 * 60) * 100
    remaining_mid = 24 * 60 - cur_mid_m

    return {
        "now": n,
        "phase": get_day_phase(hh),
        "elapsed_wake_h": elapsed_wake / 60,
        "remaining_wake_h": remaining_wake / 60,
        "pct_wake": pct_wake,
        "elapsed_mid_h": cur_mid_m / 60,
        "remaining_mid_h": remaining_mid / 60,
        "pct_mid": pct_mid,
        "wake_str": wake_str,
        "sleep_str": sleep_str,
    }