"""Report generation service."""

from datetime import datetime, timedelta
from ..models import read as read_log
from ..storage import weekly_report_path, monthly_report_path, write_text


def _collect_week(date: datetime | None = None) -> str:
    d = date or datetime.now()
    start = d - timedelta(days=d.weekday())
    parts: list[str] = []
    for i in range(7):
        day = start + timedelta(days=i)
        content = read_log(day)
        if content.strip():
            parts.append(f"### {day.strftime('%A %Y-%m-%d')}\n{content}")
    return "\n\n".join(parts) if parts else "No data for this week."


def _collect_month(date: datetime | None = None) -> str:
    d = date or datetime.now()
    parts: list[str] = []
    for day in range(1, 32):
        try:
            dt = datetime(d.year, d.month, day)
        except ValueError:
            break
        content = read_log(dt)
        if content.strip():
            parts.append(f"### {dt.strftime('%d %A')}\n{content}")
    return "\n\n".join(parts) if parts else "No data for this month."


def weekly(date: datetime | None = None) -> str:
    d = date or datetime.now()
    iso = d.isocalendar()
    week_id = f"{iso[0]}-W{iso[1]:02d}"
    data = _collect_week(d)
    path = weekly_report_path(d)
    summary = f"# Weekly Report — {week_id}\n\n## Summary\n\n{data}"
    write_text(path, summary)
    return f"Weekly report saved: {path}\n\n{data}"


def monthly(date: datetime | None = None) -> str:
    d = date or datetime.now()
    month_id = d.strftime("%Y-%m")
    data = _collect_month(d)
    path = monthly_report_path(d)
    summary = f"# Monthly Report — {month_id}\n\n## Summary\n\n{data}"
    write_text(path, summary)
    return f"Monthly report saved: {path}\n\n{data}"