"""Habit tracking domain model."""

from datetime import datetime, timedelta
from typing import Any

from ..storage import habit_log_path, read_text, write_text


def _ensure() -> str:
    path = habit_log_path()
    if not path.exists():
        header = (
            "# Habit Tracker\n\n"
            "| Habit | Streak | Best | Last Done | History (recent 7) |\n"
            "|-------|--------|------|-----------|--------------------|\n"
        )
        write_text(path, header)
    return read_text(path)


def track(habit: str, date: datetime | None = None) -> str:
    """Log a habit completion for today."""
    d = date or datetime.now()
    today_str = d.strftime("%Y-%m-%d")
    content = _ensure()

    lines = content.splitlines()
    new_lines: list[str] = []
    found = False

    for line in lines:
        if f"| {habit} |" in line:
            found = True
            parts = [p.strip() for p in line.strip("|").split("|")]
            while len(parts) < 5:
                parts.append("")
            name, streak_s, best_s, last_done, history = (
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
            )
            streak = int(streak_s) if streak_s.isdigit() else 0
            best = int(best_s) if best_s.isdigit() else 0
            hist = [h.strip() for h in history.split(",") if h.strip()]

            if last_done == today_str:
                new_lines.append(line)
                continue

            yesterday = (d - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_done == yesterday:
                streak += 1
            elif last_done != today_str:
                streak = 1

            best = max(best, streak)
            hist.append(today_str)
            hist = hist[-7:]
            hist_str = ", ".join(hist)
            new_lines.append(f"| {name} | {streak} | {best} | {today_str} | {hist_str} |")
        else:
            new_lines.append(line)

    if not found:
        hist_str = today_str
        new_lines.append(f"| {habit} | 1 | 1 | {today_str} | {hist_str} |")

    write_text(habit_log_path(), "\n".join(new_lines) + "\n")
    streak_val = 0
    for line in new_lines:
        if f"| {habit} |" in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].isdigit():
                streak_val = int(parts[1])
    fire = "🔥" if streak_val >= 3 else ""
    return f"Habit logged: {habit} — streak: {streak_val} days {fire}"


def show_all() -> str:
    """Get the full habit table."""
    return _ensure()