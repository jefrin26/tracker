"""File system storage operations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import get_tracker_home

# Backward compat: expose TRACKER_HOME for code/tests that patch it directly
# This will be kept in sync via _resolve_home()
TRACKER_HOME = get_tracker_home()
_ORIG_STORAGE_HOME = TRACKER_HOME


def _resolve_home() -> Path:
    """Resolve current tracker home, respecting patched globals for backward compat."""
    # Check if this module's TRACKER_HOME was patched (tests do `fs.TRACKER_HOME = Path(tmp)`)
    current = globals().get("TRACKER_HOME", _ORIG_STORAGE_HOME)
    if isinstance(current, Path) and current != _ORIG_STORAGE_HOME:
        # If patched to a different value, use it
        # Also sync config global so other modules see it
        try:
            import tracker.config as cfg

            if cfg.TRACKER_HOME != current:
                cfg.TRACKER_HOME = current
                cfg.CONFIG_PATH = current / "config.json"
        except Exception:
            pass
        return current
    return get_tracker_home()


def daily_log_path(date: datetime | None = None) -> Path:
    """Get path for a daily log file."""
    d = date or datetime.now()
    p = _resolve_home() / "daily" / str(d.year) / f"{d.month:02d}"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{d.strftime('%Y-%m-%d')}.md"


def habit_log_path() -> Path:
    """Get path for habit log."""
    p = _resolve_home() / "habits"
    p.mkdir(parents=True, exist_ok=True)
    return p / "habits.md"


def day_context_path(date: datetime | None = None) -> Path:
    """Get path for day context JSON."""
    d = date or datetime.now()
    p = _resolve_home() / "day_context"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{d.strftime('%Y-%m-%d')}.json"


def weekly_report_path(date: datetime | None = None) -> Path:
    """Get path for weekly report."""
    d = date or datetime.now()
    iso = d.isocalendar()
    week_id = f"{iso[0]}-W{iso[1]:02d}"
    p = _resolve_home() / "weekly"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{week_id}.md"


def monthly_report_path(date: datetime | None = None) -> Path:
    """Get path for monthly report."""
    d = date or datetime.now()
    month_id = d.strftime("%Y-%m")
    p = _resolve_home() / "monthly"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{month_id}.md"


def project_path(name: str) -> Path:
    """Get path for a project directory."""
    p = _resolve_home() / "projects" / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def export_path(date: datetime | None = None) -> Path:
    """Get path for JSON export."""
    d = date or datetime.now()
    p = _resolve_home() / "export"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{d.strftime('%Y-%m-%d')}.json"


def read_text(path: Path) -> str:
    """Read file as text, return empty string if not exists."""
    if not path.exists():
        return ""
    return path.read_text()


def write_text(path: Path, content: str) -> None:
    """Write text to file, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def read_json(path: Path) -> dict[str, Any]:
    """Read JSON file, return empty dict if not exists or invalid."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write dict as JSON to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))