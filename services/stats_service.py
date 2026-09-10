"""Statistics service."""

from datetime import datetime, timedelta
from ..models import read as read_log


def _total_minutes(date: datetime | None = None) -> int:
    content = read_log(date)
    total = 0
    for line in content.splitlines():
        if line.startswith("|") and "---" not in line and "Time" not in line and "Start" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            dur = None
            # New format: | Start | End | Activity | Duration | Type | Notes | → duration at index 3
            if len(parts) >= 6 and ":" in parts[0] and ":" in parts[1]:
                dur = parts[3].replace("m", "").strip()
            elif len(parts) >= 3:
                # Old format fallback: | Time | Activity | Duration | Type | Notes |
                dur = parts[2].replace("m", "").strip()
            if dur and dur.isdigit():
                total += int(dur)
    return total


def today() -> str:
    mins = _total_minutes()
    hours = mins / 60
    entries = sum(
        1
        for line in read_log().splitlines()
        if line.startswith("|") and "---" not in line and "Time" not in line and "Start" not in line
    )
    from ..config import get_config
    target = get_config().get("daily_target_hours", 4)
    pct = (hours / target * 100) if target else 0
    bar_len = 20
    filled = int(bar_len * min(pct, 100) / 100)
    bar = f"{'█' * filled}{'░' * (bar_len - filled)}"
    return (
        f"Today: {hours:.1f}h logged ({entries} entries)\n"
        f"Target: {target}h ({pct:.0f}%)\n"
        f"Progress: [{bar}]"
    )


def week() -> str:
    d = datetime.now()
    start = d - timedelta(days=d.weekday())
    total = 0
    day_totals: list[tuple[str, int]] = []
    for i in range(7):
        day = start + timedelta(days=i)
        m = _total_minutes(day)
        total += m
        day_totals.append((day.strftime("%a"), m))
    hours = total / 60
    best = max(day_totals, key=lambda x: x[1])
    lines = [
        f"Week total: {hours:.1f}h",
        f"Best day: {best[0]} ({best[1]/60:.1f}h)",
        "",
        "Daily breakdown:",
    ]
    for name, m in day_totals:
        h = m / 60
        bar_len = 15
        max_m = max(x[1] for x in day_totals) or 1
        filled = int(bar_len * m / max_m)
        lines.append(f"  {name:>3} {h:5.1f}h {'█' * filled}")
    return "\n".join(lines)


def all() -> str:
    return today() + "\n\n" + week()