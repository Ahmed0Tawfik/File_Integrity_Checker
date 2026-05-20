"""
reporter.py — Plain-text report formatter and log writer.
"""

import os
import re
import time
from pathlib import Path


def _strip_ansi(text: str) -> str:
    """Removes ANSI escape codes from a string."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def build_plain_report(diff_result: dict) -> str:
    """
    Builds a plain-text integrity report string from a verify_integrity() result.
    """
    s = diff_result.get("summary", {})
    lines = [
        "=" * 72,
        "  FILE INTEGRITY REPORT",
        f"  Generated : {s.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S'))}",
        f"  Directory : {s.get('directory', 'N/A')}",
        f"  Baseline  : {s.get('baseline', 'N/A')}",
        f"  Algorithm : {s.get('algorithm', 'N/A').upper()}",
        f"  Scan time : {s.get('elapsed_s', 0)} s",
        "=" * 72,
        "",
        f"  SUMMARY — {s.get('total', 0)} files",
        f"    Unchanged : {s.get('unchanged', 0)}",
        f"    Modified  : {s.get('modified', 0)}",
        f"    Deleted   : {s.get('deleted', 0)}",
        f"    New       : {s.get('new', 0)}",
        "",
    ]

    def section(title, items, fields):
        if not items:
            return
        lines.append(f"── {title} ({len(items)}) " + "─" * max(0, 60 - len(title)))
        for item in items:
            lines.append(f"  [{item.get('severity','?'):8s}] {item['path']}")
            for label, key in fields:
                val = item.get(key)
                if val is not None and val != "":
                    lines.append(f"             {label}: {val}")
        lines.append("")

    section("MODIFIED", diff_result.get("modified", []),
            [("Old hash", "old_hash"), ("New hash", "new_hash")])
    section("DELETED",  diff_result.get("deleted", []),
            [("Hash", "old_hash")])
    section("NEW",      diff_result.get("new", []),
            [("Hash", "new_hash")])
    section("UNCHANGED", diff_result.get("unchanged", []), [])

    lines.append("=" * 72)
    return "\n".join(lines)


def save_log(diff_result: dict, log_dir: str = "logs") -> str:
    """
    Writes the full report to a timestamped log file.

    Returns:
        Absolute path to the written log file.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_path = Path(log_dir) / f"integrity_{timestamp}.log"

    report_text = build_plain_report(diff_result)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return str(log_path.resolve())


def parse_log_history(log_dir: str = "logs") -> list:
    """
    Parses previous log files and returns a mini-history list of dicts.
    Each dict: { path, timestamp, modified, deleted, new, unchanged }
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return []

    history = []
    for log_file in sorted(log_path.glob("integrity_*.log"), reverse=True):
        entry = {
            "path":      str(log_file.resolve()),
            "name":      log_file.name,
            "timestamp": log_file.stem.replace("integrity_", ""),
            "modified":  0,
            "deleted":   0,
            "new":       0,
            "unchanged": 0,
        }
        try:
            content = log_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                for key in ("Modified", "Deleted", "New", "Unchanged"):
                    if f"{key}  :" in line or f"{key} :" in line:
                        try:
                            val = int(line.split(":")[-1].strip())
                            entry[key.lower()] = val
                        except ValueError:
                            pass
        except OSError:
            pass
        history.append(entry)

    return history
