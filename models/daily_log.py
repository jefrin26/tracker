"""Daily log domain model."""

import re
from datetime import datetime
from typing import Any

from ..storage import daily_log_path, read_text, write_text
from ..utils import today_str


TYPES = ("work", "study", "rest", "eat", "social", "exercise", "chores", "wasted")


def template(date_str: str) -> str:
    """Generate empty daily log template."""
    return f"""# Daily Log — {date_str}

## 🎯 Goals
- [ ] 

## ⏰ Time Log
| Time | Activity | Duration | Type | Notes |
|------|----------|----------|------|-------|

## 🌙 Sleep
| Bedtime | Wake Time | Uptime | Notes |
|---------|-----------|--------|-------|

## 📅 Day Context
- Type: _normal_ (exam / college / holiday / normal)
- Notes: 

## ✅ Accomplished


## 💡 Learnings


## 🏆 Wins


## 😤 Struggles


## 📊 Scores
- Productivity: _/10
- Energy: _/10
- Mood: _/10

## 📝 Raw Notes

"""


def ensure(date: datetime | None = None) -> None:
    """Create today's log file if it doesn't exist."""
    path = daily_log_path(date)
    if not path.exists():
        d = date or datetime.now()
        write_text(path, template(d.strftime("%Y-%m-%d")))


def read(date: datetime | None = None) -> str:
    """Read daily log content."""
    return read_text(daily_log_path(date))


def write(content: str, date: datetime | None = None) -> None:
    """Write daily log content."""
    write_text(daily_log_path(date), content)


def add_activity(
    activity: str,
    duration: int,
    act_type: str,
    time_str: str | None = None,
    notes: str = "",
    date: datetime | None = None,
) -> str:
    """Append a row to the time-log table."""
    ensure(date)
    content = read(date)
    t = time_str or datetime.now().strftime("%H:%M")
    row = f"| {t} | {activity} | {duration}m | {act_type} | {notes} |"

    lines = content.splitlines()
    new_lines: list[str] = []
    inserted = False
    in_time_log = False
    for line in lines:
        if line.startswith("## ⏰ Time Log"):
            in_time_log = True
        if line.startswith("## ") and in_time_log and not line.startswith("## ⏰ Time Log"):
            in_time_log = False
        # Insert after the table separator row
        if in_time_log and line.strip().startswith("|") and "---" in line:
            new_lines.append(line)
            new_lines.append(row)
            inserted = True
            continue
        new_lines.append(line)
    if not inserted:
        marker = "## ✅ Accomplished"
        content = "\n".join(new_lines)
        if marker in content:
            content = content.replace(marker, row + "\n" + marker)
        else:
            content += row
    else:
        content = "\n".join(new_lines)

    write(content, date)

    reaction = f"Logged: {activity} ({duration}m) — {act_type}"
    if act_type == "wasted":
        reaction += "\n😤 Bruh, {duration} mins gone. You know better."
    elif duration >= 60:
        reaction += "\n🔥 Over an hour — solid commitment."
    return reaction


def add_goal(goal: str, date: datetime | None = None) -> str:
    """Add a goal to today's log."""
    ensure(date)
    content = read(date)
    new_line = f"- [ ] {goal}\n"
    marker = "## 🎯 Goals"
    if marker in content:
        idx = content.index(marker) + len(marker)
        content = content[:idx] + "\n" + new_line + content[idx:].lstrip("\n")
    else:
        content += "\n## 🎯 Goals\n" + new_line
    write(content, date)
    return f"Goal added: {goal}"


def done_goal(goal: str, date: datetime | None = None) -> str:
    """Mark a goal as complete."""
    content = read(date)
    if not content:
        return "No log found for today."
    target = f"- [ ] {goal}"
    replacement = f"- [x] {goal}"
    if target in content:
        content = content.replace(target, replacement, 1)
        write(content, date)
        return f"Completed: {goal}"
    return f"Goal '{goal}' not found."


def set_scores(
    productivity: int, energy: int, mood: int, date: datetime | None = None
) -> str:
    """Update the three score fields."""
    content = read(date)
    if not content:
        return "No log found."
    for label, val in [
        ("Productivity", productivity),
        ("Energy", energy),
        ("Mood", mood),
    ]:
        pattern = rf"- {label}: _/10"
        replacement = f"- {label}: {val}/10"
        content = re.sub(pattern, replacement, content)
    write(content, date)
    return "Scores updated."


def display(date: datetime | None = None) -> str:
    """Get formatted log for display."""
    d = date or datetime.now()
    content = read(date)
    if not content.strip():
        return f"No log for {d.strftime('%Y-%m-%d')}."
    return content


def parse_entries(date: datetime | None = None) -> dict[str, Any]:
    """Parse log into structured data for AI prompts."""
    content = read(date)
    result: dict[str, Any] = {
        "activities": [],
        "goals": [],
        "completed": [],
        "scores": {"productivity": 0, "energy": 0, "mood": 0},
        "accomplished": "",
        "learnings": "",
        "wins": "",
        "struggles": "",
    }
    if not content:
        return result

    for line in content.splitlines():
        if line.startswith("|") and "---" not in line and "Time" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4:
                result["activities"].append(
                    {
                        "time": parts[0],
                        "activity": parts[1],
                        "duration": parts[2],
                        "type": parts[3],
                        "notes": parts[4] if len(parts) > 4 else "",
                    }
                )
        if line.strip().startswith("- [ ]"):
            result["goals"].append(line.strip().lstrip("- [ ] ").strip())
        if line.strip().startswith("- [x]"):
            result["completed"].append(line.strip().lstrip("- [x] ").strip())
        for key in ("productivity", "energy", "mood"):
            m = re.search(rf"- {key.title()}: (\d+)/10", line, re.I)
            if m:
                result["scores"][key] = int(m.group(1))
    return result