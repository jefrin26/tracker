"""Main tracker service - orchestrates all sub-services."""

from ..ai import create_client
from ..config import ensure_config
from ..models import ensure as ensure_log
from ..storage import daily_log_path


class TrackerService:
    """Main orchestrator - wires all sub-systems together."""

    def __init__(self) -> None:
        self._config: dict | None = None
        self._ai = None

    def _load(self) -> None:
        if self._config is None:
            self._config = ensure_config()
            if self._config.get("api_key"):
                self._ai = create_client()

    @property
    def config(self) -> dict:
        self._load()
        return self._config

    @property
    def ai(self):
        self._load()
        return self._ai

    def init(self, path: str | None = None) -> None:
        """Initialize tracker folders and config.

        Handles custom locations:
        - If `path` is provided (via --path), uses it directly (non-interactive).
        - Otherwise interactively asks (a) whether user has existing data
          and (b) where to create/store tracker.
        """
        from pathlib import Path
        from ..config import get_tracker_home, set_tracker_home, DEFAULT_HOME

        from ..utils import heading, ok, warn, dim

        heading("🔧 Initializing tracker")

        # Determine target directory
        target: Path | None = None

        if path:
            # Non-interactive: use provided path directly
            target = Path(path).expanduser().resolve()
            set_tracker_home(target)
            ok(f"Using tracker home: {target}")
        else:
            # Interactive flow
            current = get_tracker_home()
            default_str = str(DEFAULT_HOME)
            # Show current if pointer already set
            try:
                from ..config import POINTER_FILE

                if POINTER_FILE.exists() or current != DEFAULT_HOME:
                    print(dim(f"Current tracker location: {current}"))
            except Exception:
                pass

            # 1. Ask for existing location
            try:
                ans = input("Do you have an existing tracker directory? (y/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                ans = "n"
            if ans in ("y", "yes"):
                try:
                    existing = input("Enter path to existing tracker directory: ").strip()
                except (EOFError, KeyboardInterrupt):
                    existing = ""
                if existing:
                    p = Path(existing).expanduser().resolve()
                    if p.exists() and p.is_dir():
                        # Accept even if config missing; we will create config if needed
                        target = p
                        set_tracker_home(target)
                        ok(f"Using existing tracker at {target}")
                        if (target / "config.json").exists():
                            print(dim("Found existing config — will reuse"))
                    else:
                        warn(f"Path '{p}' does not exist or is not a directory — will create new one.")
                        # Fall through to creation prompt
                        target = None
                else:
                    warn("No path entered — will create new tracker.")
                    target = None

            # 2. If not using existing, ask where to create
            if target is None:
                try:
                    loc = input(f"Where to store tracker data? (default: {default_str}): ").strip()
                except (EOFError, KeyboardInterrupt):
                    loc = ""
                if not loc:
                    target = DEFAULT_HOME
                else:
                    target = Path(loc).expanduser().resolve()
                # Persist choice
                set_tracker_home(target)
                if target.exists():
                    ok(f"Using tracker home: {target} (already exists)")
                else:
                    ok(f"Tracker home will be created at: {target}")

        # At this point target is set and pointer file written
        # Ensure directories
        home = get_tracker_home()
        for sub in [
            "daily",
            "weekly",
            "monthly",
            "projects",
            "habits",
            "export",
            "day_context",
        ]:
            (home / sub).mkdir(parents=True, exist_ok=True)
        ok(f"Created {home}/")

        cfg_path = home / "config.json"
        if not cfg_path.exists():
            from ..config import save_config, DEFAULT_CONFIG

            save_config(DEFAULT_CONFIG)
            try:
                api = input("🔑 Enter your OpenRouter API key (or leave blank): ").strip()
            except (EOFError, KeyboardInterrupt):
                api = ""
            if api:
                cfg = DEFAULT_CONFIG.copy()
                cfg["api_key"] = api
                save_config(cfg)
            ok("Config saved!")
        else:
            warn("Config already exists — skipping.")

        ensure_log()
        ok(f"Today's log ready: {daily_log_path().name}")
        print(
            "\n🚀 Ready! Try:\n"
            "   tracker log \"Study networking\" 09:00 10:30 work\n"
            "   tracker goal \"Learn subnetting\"\n"
            "   tracker review\n"
            "   tracker sleep --bedtime 23:00 --wakeup 07:00\n"
            "   tracker special exam --notes \"Final exam\"\n"
        )

    def today(self) -> str:
        from ..models import display
        return display()

    def yesterday(self) -> str:
        from ..models import display
        from datetime import datetime, timedelta
        return display(datetime.now() - timedelta(days=1))

    def stats(self) -> str:
        from .stats_service import all as all_stats
        return all_stats()

    def report(self) -> None:
        print(self.stats())
        print()
        print(self.today())
        print()
        from ..models import show_habits
        print(show_habits())

    def search(self, keyword: str) -> str:
        from .search_service import SearchService
        return SearchService().search(keyword)

    def export(self, fmt: str = "json") -> str:
        from .export_service import export
        return export(fmt)