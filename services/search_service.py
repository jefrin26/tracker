"""Search service."""

from ..config import get_tracker_home


def search(keyword: str) -> str:
    results: list[str] = []
    daily_root = get_tracker_home() / "daily"
    if not daily_root.exists():
        return "No logs found."
    kw = keyword.lower()
    for md in sorted(daily_root.rglob("*.md")):
        content = md.read_text()
        if kw in content.lower():
            matches = [
                ln.strip()
                for ln in content.splitlines()
                if kw in ln.lower() and ln.strip()
            ]
            date_label = md.stem
            results.append(f"📅 {date_label} — {len(matches)} match(es)")
            for m in matches[:5]:
                results.append(f"   {m}")
    return "\n".join(results) if results else f"No matches for '{keyword}'."