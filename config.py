"""Configuration management."""

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_HOME = Path.home() / "tracker"
# Pointer file that remembers custom location (XDG-compatible)
POINTER_FILE = Path.home() / ".config" / "tracker" / "location"
LEGACY_POINTER_FILE = Path.home() / ".tracker_location"

# Mutable globals for runtime override (e.g., tests patch TRACKER_HOME directly)
TRACKER_HOME: Path = DEFAULT_HOME
CONFIG_PATH: Path = TRACKER_HOME / "config.json"


def get_tracker_home() -> Path:
    """Resolve tracker home dynamically.

    Priority:
    1. $TRACKER_HOME env var (if set)
    2. Explicitly patched `TRACKER_HOME` global (for tests / runtime override)
    3. Pointer file at ~/.config/tracker/location (or legacy ~/.tracker_location)
    4. Default ~/tracker
    """
    # 1. Env var
    env = os.getenv("TRACKER_HOME")
    if env:
        return Path(env).expanduser().resolve()
    # 2. Patched global (detect if someone did `config.TRACKER_HOME = Path(...)`)
    # Use globals to avoid issues with import-time binding
    current = globals().get("TRACKER_HOME", DEFAULT_HOME)
    if isinstance(current, Path) and current != DEFAULT_HOME:
        return current.resolve() if current.is_absolute() else (Path.cwd() / current).resolve()
    # 3. Pointer files
    for pointer in (POINTER_FILE, LEGACY_POINTER_FILE):
        if pointer.exists():
            try:
                txt = pointer.read_text().strip()
                if txt:
                    p = Path(txt).expanduser()
                    # Resolve relative to home if not absolute
                    if not p.is_absolute():
                        p = Path.home() / p
                    return p.resolve()
            except Exception:
                continue
    # 4. Default
    return DEFAULT_HOME


def get_config_path() -> Path:
    """Get config.json path for current tracker home."""
    return get_tracker_home() / "config.json"


def set_tracker_home(path: str | Path) -> Path:
    """Persist custom tracker home location.

    Writes pointer file and updates runtime globals.
    Returns resolved Path.
    """
    p = Path(path).expanduser().resolve()
    # Update globals
    global TRACKER_HOME, CONFIG_PATH
    TRACKER_HOME = p
    CONFIG_PATH = p / "config.json"
    # Persist pointer
    try:
        POINTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        POINTER_FILE.write_text(str(p))
    except Exception:
        # Fallback to legacy pointer if parent not writable
        try:
            LEGACY_POINTER_FILE.write_text(str(p))
        except Exception:
            pass
    return p


def _resolve_config_path() -> Path:
    """Internal helper to get current config path (dynamic)."""
    return get_config_path()


DEFAULT_CONFIG: dict[str, Any] = {
    "api_key": "",
    "daily_target_hours": 4,
    "sleep_time": "23:00",
    "wake_time": "07:00",
    "habit_streak_reset_hours": 24,
    "review_time": "21:00",
    "name": "Your Name",
    "special_day": {},
    "bedtime": None,
    "wakeup": None,
    "model": "openrouter/free",
}


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    cfg_path = _resolve_config_path()
    if not cfg_path.exists():
        raise FileNotFoundError("Run 'tracker init' first.")
    with open(cfg_path) as f:
        return json.load(f)


def save_config(cfg: dict[str, Any]) -> None:
    """Save configuration to file."""
    cfg_path = _resolve_config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)


def ensure_config() -> dict[str, Any]:
    """Ensure config exists, creating defaults if needed."""
    cfg_path = _resolve_config_path()
    if not cfg_path.exists():
        save_config(DEFAULT_CONFIG)
    return load_config()


def get_config() -> dict[str, Any]:
    """Get current config (lazy load)."""
    return load_config()