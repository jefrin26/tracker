"""Project management domain model."""

from pathlib import Path

from ..storage import project_path, read_text, write_text


def open_project(name: str) -> str:
    """Open or create a project, return progress.md content."""
    base = project_path(name)
    created = False
    for fname in ("progress.md", "milestones.md", "notes.md"):
        fp = base / fname
        if not fp.exists():
            fp.write_text(f"# {name} — {fname.replace('.md', '').title()}\n\n")
            created = True
    if created:
        print(f"✅ Created project '{name}' with files.")
    return read_text(base / "progress.md")