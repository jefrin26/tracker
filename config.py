"""Configuration management."""

import json
from pathlib import Path
from typing import Any

TRACKER_HOME = Path.home() / "tracker"

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

CONFIG_PATH = TRACKER_HOME / "config.json"


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Run 'tracker init' first.")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(cfg: dict[str, Any]) -> None:
    """Save configuration to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def ensure_config() -> dict[str, Any]:
    """Ensure config exists, creating defaults if needed."""
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
    return load_config()


def get_config() -> dict[str, Any]:
    """Get current config (lazy load)."""
    return load_config()