"""Read-only recursive discovery of candidate Winamax text exports."""

from pathlib import Path

CANDIDATE_SUFFIXES = {".txt", ".log"}


def scan_history_files(root: Path) -> list[Path]:
    """Return candidate regular files without ever modifying source files."""
    root = root.expanduser()
    if not root.exists():
        raise FileNotFoundError(f"History path does not exist: {root}")
    if root.is_file():
        return [root] if root.suffix.lower() in CANDIDATE_SUFFIXES else []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in CANDIDATE_SUFFIXES
    )
