"""Export service."""

from datetime import datetime
from ..models import parse_entries
from ..storage import export_path, write_json


def export(fmt: str = "json", date: datetime | None = None) -> str:
    if fmt != "json":
        return f"Export format '{fmt}' not yet supported (use json)."
    d = date or datetime.now()
    data = parse_entries(d)
    data["date"] = d.strftime("%Y-%m-%d")
    path = export_path(d)
    write_json(path, data)
    return f"Exported to {path}"