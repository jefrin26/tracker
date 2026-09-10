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
| Start | End | Activity | Duration | Type | Notes |
|-------|-------|----------|----------|------|-------|

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
    start: str | int,
    end: str,
    act_type: str = "work",
    notes: str = "",
    date: datetime | None = None,
) -> str:
    """Append a row to the time-log table using start/end times.

    Calculates duration automatically and stores start, end, and duration.
    Handles overnight sessions (end < start → next day).

    Backward-compatible: if `start` is an int/digit (duration) and `end`
    is a type string, treats as legacy call `add_activity(activity, duration, type)`
    and synthesizes start/end from current time.
    """
    from ..utils.time_utils import duration_between, parse_time, to_minutes, to_hhmm, now_hhmm

    # Backward compatibility: legacy duration-based call
    # e.g. add_activity("Study", 30, "work") or add_activity("Study", "30", "work")
    if isinstance(start, int) or (isinstance(start, str) and start.strip().isdigit()):
        # Check if `end` looks like a type (not a time)
        if isinstance(end, str) and (end in TYPES or not parse_time(end)):
            duration_legacy = int(str(start).strip())  # type: ignore
            legacy_type = end if end in TYPES else act_type
            # `act_type` in this legacy context may hold time_str or notes
            legacy_notes = notes
            legacy_time_str = None
            # If act_type looks like a time, it was legacy time_str
            if isinstance(act_type, str) and parse_time(act_type):
                legacy_time_str = act_type
            elif isinstance(act_type, str) and act_type not in TYPES and act_type != "work" and act_type:
                # May be notes passed positionally as 4th arg (legacy: time_str omitted, notes as 4th)
                # e.g. add_activity("Study", 30, "work", "my notes")
                if not notes:
                    legacy_notes = act_type
            # Use legacy time_str if provided, else now
            start_time = legacy_time_str or now_hhmm()
            s_pt = parse_time(start_time)
            if not s_pt:
                start_time = now_hhmm()
                s_pt = parse_time(start_time)
            assert s_pt is not None
            start_m = to_minutes(*s_pt)
            end_m = (start_m + duration_legacy) % (24 * 60)
            end_time = to_hhmm(end_m)
            # Reassign to new style
            start = start_time
            end = end_time
            act_type = legacy_type
            notes = legacy_notes

    # Ensure start/end are strings now
    start = str(start)
    end = str(end)

    ensure(date)
    content = read(date)

    # Validate times
    if not parse_time(start):
        return f"Invalid start time '{start}'. Use HH:MM (e.g. 09:00)."
    if not parse_time(end):
        return f"Invalid end time '{end}'. Use HH:MM (e.g. 10:30)."

    duration = duration_between(start, end)
    if duration is None:
        return f"Invalid time range: {start} → {end}. End must be after start."

    row = f"| {start} | {end} | {activity} | {duration}m | {act_type} | {notes} |"

    # Migrate old header if present (backward compatibility)
    old_header = "| Time | Activity | Duration | Type | Notes |"
    new_header = "| Start | End | Activity | Duration | Type | Notes |"
    old_sep = "|------|----------|----------|------|-------|"
    new_sep = "|-------|-------|----------|----------|------|-------|"
    has_old_header = old_header in content
    if has_old_header:
        content = content.replace(old_header, new_header)
        content = content.replace(old_sep, new_sep)

    lines = content.splitlines()
    new_lines: list[str] = []
    inserted = False
    in_time_log = False
    for line in lines:
        # Migrate old data rows to new format (for backward compatibility)
        # Always check: old rows have 5 cols, new have 6 — convert 5→6 using start+duration
        if in_time_log and line.strip().startswith("|") and "---" not in line and "Start" not in line and "Time" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            # Old format has 5 cols: Time | Activity | Duration | Type | Notes
            # Detect old rows: 5 parts, first part is time (contains :), third part ends with m
            if len(parts) == 5 and ":" in parts[0] and parts[2].endswith("m"):
                try:
                    from ..utils.time_utils import parse_time as _pt, to_minutes as _tm, to_hhmm as _th
                    dur_str = parts[2].replace("m", "").strip()
                    if dur_str.isdigit():
                        dur_val = int(dur_str)
                        pt = _pt(parts[0])
                        if pt:
                            start_m = _tm(*pt)
                            end_m = (start_m + dur_val) % (24 * 60)
                            end_str = _th(end_m)
                            line = f"| {parts[0]} | {end_str} | {parts[1]} | {parts[2]} | {parts[3]} | {parts[4]} |"
                except Exception:
                    pass
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

    reaction = f"Logged: {activity} ({start} → {end}, {duration}m) — {act_type}"
    if act_type == "wasted":
        reaction += f"\n😤 Bruh, {duration} mins gone. You know better."
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
    """Parse log into structured data for AI prompts. Handles both old (Time) and new (Start/End) formats."""
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
        if line.startswith("|") and "---" not in line and "Time" not in line and "Start" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            # New format: | Start | End | Activity | Duration | Type | Notes |  (6 cols)
            if len(parts) >= 6 and ":" in parts[0] and ":" in parts[1]:
                result["activities"].append(
                    {
                        "start": parts[0],
                        "end": parts[1],
                        "time": f"{parts[0]} → {parts[1]}",
                        "activity": parts[2],
                        "duration": parts[3],
                        "type": parts[4],
                        "notes": parts[5] if len(parts) > 5 else "",
                    }
                )
            elif len(parts) >= 4:
                # Old format: | Time | Activity | Duration | Type | Notes |
                result["activities"].append(
                    {
                        "start": parts[0],
                        "end": "",
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