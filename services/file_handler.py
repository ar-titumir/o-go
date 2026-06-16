"""
services/file_handler.py
------------------------
All file-system operations the agent is allowed to perform.

SAFETY RULE: every path is resolved and checked to be inside
AGENT_WORKSPACE_DIR before any I/O happens.  Anything outside
the sandbox raises PermissionError immediately.
"""

import shutil
from pathlib import Path
from typing import Optional

from config import AGENT_WORKSPACE_DIR
from utils import get_logger

log = get_logger(__name__)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _safe_path(relative_or_absolute: str | Path) -> Path:
    """
    Resolve a path and verify it is inside the workspace sandbox.
    Always use this before touching the filesystem.
    """
    target = (AGENT_WORKSPACE_DIR / relative_or_absolute).resolve()

    # resolve() removes ".." tricks — still check explicitly
    if not str(target).startswith(str(AGENT_WORKSPACE_DIR)):
        raise PermissionError(
            f"Access denied: '{target}' is outside the workspace "
            f"'{AGENT_WORKSPACE_DIR}'"
        )
    return target


# ── Public API ─────────────────────────────────────────────────────────────────

def list_files(subdir: str = ".") -> list[str]:
    """
    Return relative paths of all files (recursive) inside *subdir*.
    subdir defaults to the workspace root.
    """
    base = _safe_path(subdir)
    if not base.exists():
        return []
    return [
        str(p.relative_to(AGENT_WORKSPACE_DIR))
        for p in sorted(base.rglob("*"))
        if p.is_file()
    ]


def read_file(relative_path: str) -> str:
    """Read a text file and return its contents."""
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {relative_path}")
    log.debug("read_file: %s", path)
    return path.read_text(encoding="utf-8")


def write_file(relative_path: str, content: str, overwrite: bool = True) -> Path:
    """
    Write *content* to a text file.
    Creates parent directories as needed.
    If overwrite=False and file exists, raises FileExistsError.
    """
    path = _safe_path(relative_path)
    if not overwrite and path.exists():
        raise FileExistsError(f"File already exists: {relative_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    log.info("write_file: %s (%d bytes)", path, len(content))
    return path


def append_file(relative_path: str, content: str) -> Path:
    """Append *content* to an existing file (creates if absent)."""
    path = _safe_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)
    log.info("append_file: %s", path)
    return path


def delete_file(relative_path: str) -> None:
    """Delete a single file."""
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {relative_path}")
    if path.is_dir():
        raise IsADirectoryError(f"'{relative_path}' is a directory — use delete_dir()")
    path.unlink()
    log.info("delete_file: %s", path)


def delete_dir(relative_path: str) -> None:
    """Recursively delete a directory and all its contents."""
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"No such directory: {relative_path}")
    shutil.rmtree(path)
    log.info("delete_dir: %s", path)


def make_dir(relative_path: str) -> Path:
    """Create a directory (and parents) inside the workspace."""
    path = _safe_path(relative_path)
    path.mkdir(parents=True, exist_ok=True)
    log.info("make_dir: %s", path)
    return path


def save_bytes(relative_path: str, data: bytes) -> Path:
    """Write raw bytes to a file (for images, PDFs, etc.)."""
    path = _safe_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    log.info("save_bytes: %s (%d bytes)", path, len(data))
    return path


def read_bytes(relative_path: str) -> bytes:
    """Read raw bytes from a file."""
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {relative_path}")
    log.debug("read_bytes: %s", path)
    return path.read_bytes()


def file_info(relative_path: str) -> dict:
    """Return basic metadata about a file."""
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {relative_path}")
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path.relative_to(AGENT_WORKSPACE_DIR)),
        "size_bytes": stat.st_size,
        "is_dir": path.is_dir(),
        "absolute": str(path),
    }
