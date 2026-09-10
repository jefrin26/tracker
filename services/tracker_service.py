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

    def init(self) -> None:
        """Initialize tracker folders and config."""
        from ..utils import heading, ok, warn

        heading("🔧 Initializing tracker")
        for sub in [
            "daily",
            "weekly",
            "monthly",
            "projects",
            "habits",
            "export",
            "day_context",
        ]:
            (daily_log_path().parent.parent / sub).mkdir(parents=True, exist_ok=True)
        ok(f"Created ~/tracker/")

        cfg_path = daily_log_path().parent.parent / "config.json"
        if not cfg_path.exists():
            from ..config import save_config, DEFAULT_CONFIG
            save_config(DEFAULT_CONFIG)
            api = input("🔑 Enter your OpenRouter API key (or leave blank): ").strip()
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
            "   tracker log \"Study networking\" 30 work\n"
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