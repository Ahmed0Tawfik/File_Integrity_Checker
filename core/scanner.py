import os
import time
from pathlib import Path
from typing import Callable, Optional
from core.hasher import hash_file

SEVERITY_MAP = {
    "CRITICAL": {".exe", ".dll", ".sys", ".ko", ".so", ".dylib"},
    "HIGH":     {".py", ".js", ".sh", ".bat", ".ps1", ".rb", ".php", ".pl", ".cmd"},
    "MEDIUM":   {".conf", ".cfg", ".ini", ".json", ".yaml", ".yml", ".toml", ".xml", ".env"},
    "LOW":      {".txt", ".md", ".rst", ".log", ".csv"},
}


def get_severity(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    for level, extensions in SEVERITY_MAP.items():
        if ext in extensions:
            return level
    return "MEDIUM"


def scan_directory(
    path: str,
    algorithm: str = "sha256",
    ignore_patterns: Optional[list] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> dict:
    root = Path(path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"'{path}' is not a valid directory.")

    all_files = [f for f in root.rglob("*") if f.is_file()]

    if ignore_patterns:
        import fnmatch
        filtered = []
        for f in all_files:
            rel = str(f.relative_to(root))
            should_ignore = any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(f.name, pat)
                                for pat in ignore_patterns)
            if not should_ignore:
                filtered.append(f)
        all_files = filtered

    results = {}
    total = len(all_files)

    for idx, filepath in enumerate(all_files):
        rel_path = str(filepath.relative_to(root))

        if progress_callback:
            progress_callback(idx, total, rel_path)

        try:
            file_hash = hash_file(str(filepath), algorithm)
            stat = filepath.stat()
            results[rel_path] = {
                "hash":     file_hash,
                "size":     stat.st_size,
                "modified": stat.st_mtime,
                "severity": get_severity(rel_path),
            }
        except (PermissionError, OSError) as e:
            results[rel_path] = {
                "hash":     "ERROR",
                "size":     0,
                "modified": 0.0,
                "severity": "UNKNOWN",
                "error":    str(e),
            }

    if progress_callback:
        progress_callback(total, total, "Done")

    results["__meta__"] = {
        "algorithm":  algorithm,
        "scanned_at": time.time(),
        "root":       str(root),
        "file_count": len(results) - 1,
    }

    return results
