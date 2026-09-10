"""Sleep tracking domain model."""

import re
from datetime import datetime
from typing import Any

from ..storage import daily_log_path, read_text, write_text
from ..utils import parse_time, to_minutes, uptime_minutes, format_uptime


def _parse_time(time_str: str) -> tuple[int, int] | None:
    return parse_time(time_str)


def _update_row(content: str, bedtime: str, wake_time: str, notes: str) -> str:
    """Upsert the sleep table row."""
    up_m = uptime_minutes(bedtime, wake_time)
    uptime = format_uptime(up_m)
    row = f"| {bedtime} | {wake_time} | {uptime} | {notes} |"
    marker = "## 🌙 Sleep"
    if marker not in content:
        content += f"\n\n{marker}\n| Bedtime | Wake Time | Uptime | Notes |\n|---------|-----------|--------|-------|\n"
    lines = content.splitlines()
    new_lines: list[str] = []
    replaced = False
    in_sleep = False
    for line in lines:
        if line.startswith("## 🌙 Sleep"):
            in_sleep = True
            new_lines.append(line)
            continue
        if line.startswith("## ") and in_sleep:
            in_sleep = False
            new_lines.append(line)
            continue
        if in_sleep and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if not replaced and len(parts) >= 3 and parts[0] != "Bedtime" and parts[0] != "---":
                new_lines.append(row)
                replaced = True
            elif replaced and len(parts) >= 3 and parts[0] != "Bedtime" and parts[0] != "---":
                continue
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(row)
    return "\n".join(new_lines)


def _extract_bedtime(content: str) -> str:
    in_sleep = False
    for line in content.splitlines():
        if line.startswith("## 🌙 Sleep"):
            in_sleep = True
            continue
        if line.startswith("## ") and in_sleep:
            in_sleep = False
        if in_sleep and line.startswith("|") and "Bedtime" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 1:
                return parts[0]
    return "—"


def _extract_wake(content: str) -> str:
    in_sleep = False
    for line in content.splitlines():
        if line.startswith("## 🌙 Sleep"):
            in_sleep = True
            continue
        if line.startswith("## ") and in_sleep:
            in_sleep = False
        if in_sleep and line.startswith("|") and "Bedtime" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                return parts[1]
    return "—"


def log_bedtime(bedtime: str, notes: str = "", date: datetime | None = None) -> str:
    """Record when the user went to bed."""
    if not _parse_time(bedtime):
        return "Invalid time format. Use HH:MM (e.g. 23:00)."
    d = date or datetime.now()
    from .daily_log import ensure
    ensure(d)
    content = read_text(daily_log_path(d))
    wake_time = _extract_wake(content)
    content = _update_row(content, bedtime, wake_time, notes)
    write_text(daily_log_path(d), content)
    return f"Bedtime logged: {bedtime}"


def log_wakeup(wake_time: str, notes: str = "", date: datetime | None = None) -> str:
    """Record when the user woke up."""
    if not _parse_time(wake_time):
        return "Invalid time format. Use HH:MM (e.g. 07:00)."
    d = date or datetime.now()
    from .daily_log import ensure
    ensure(d)
    content = read_text(daily_log_path(d))
    bedtime = _extract_bedtime(content)
    content = _update_row(content, bedtime, wake_time, notes)
    write_text(daily_log_path(d), content)
    up_m = uptime_minutes(bedtime, wake_time)
    if up_m is not None:
        return f"Wake time logged: {wake_time} — uptime {up_m / 60:.1f}h"
    return f"Wake time logged: {wake_time}"


def get_today(date: datetime | None = None) -> dict[str, Any]:
    """Return today's sleep data for AI prompts."""
    d = date or datetime.now()
    content = read_text(daily_log_path(d))
    bedtime, wake_time, uptime = "—", "—", "—"
    in_sleep = False
    for line in content.splitlines():
        if line.startswith("## 🌙 Sleep"):
            in_sleep = True
            continue
        if line.startswith("## ") and in_sleep:
            in_sleep = False
        if in_sleep and line.startswith("|") and "Bedtime" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3:
                bedtime, wake_time, uptime = parts[0], parts[1], parts[2]
                break
    return {"bedtime": bedtime, "wake_time": wake_time, "uptime": uptime}