"""
verifier.py — Diffs a fresh scan against a saved baseline.
"""

import time
from pathlib import Path
from core.scanner import scan_directory
from core.baseline import load_baseline


def verify_integrity(
    directory: str,
    baseline_path: str,
    algorithm: str = None,
    ignore_patterns: list = None,
    progress_callback=None,
) -> dict:
    """
    Re-scans a directory, loads the saved baseline, and diffs the two.

    Args:
        directory:        Directory to re-scan.
        baseline_path:    Path to the .json baseline file.
        algorithm:        Override the algorithm (defaults to what was stored in baseline).
        ignore_patterns:  Glob patterns to skip.
        progress_callback: Optional callable(current, total, filename).

    Returns:
        dict with keys:
            unchanged: list of file dicts
            modified:  list of file dicts
            deleted:   list of file dicts
            new:       list of file dicts
            summary:   dict with counts + timing
    """
    baseline = load_baseline(baseline_path)
    meta = baseline.get("__meta__", {})

    # Honour algorithm stored in baseline unless caller overrides
    algo = algorithm or meta.get("algorithm", "sha256")

    # Re-scan
    t0 = time.time()
    current = scan_directory(directory, algo, ignore_patterns, progress_callback)
    elapsed = round(time.time() - t0, 2)

    # Strip __meta__ from both for comparison
    baseline_files = {k: v for k, v in baseline.items() if k != "__meta__"}
    current_files  = {k: v for k, v in current.items()  if k != "__meta__"}

    baseline_keys = set(baseline_files.keys())
    current_keys  = set(current_files.keys())

    unchanged = []
    modified  = []
    deleted   = []
    new_files = []

    # Deleted — in baseline but not in current scan
    for path in sorted(baseline_keys - current_keys):
        deleted.append({
            "path":     path,
            "status":   "Deleted",
            "severity": baseline_files[path].get("severity", "MEDIUM"),
            "old_hash": baseline_files[path].get("hash", ""),
            "new_hash": "",
            "old_size": baseline_files[path].get("size", 0),
            "new_size": 0,
        })

    # New — in current scan but not in baseline
    for path in sorted(current_keys - baseline_keys):
        new_files.append({
            "path":     path,
            "status":   "New",
            "severity": current_files[path].get("severity", "MEDIUM"),
            "old_hash": "",
            "new_hash": current_files[path].get("hash", ""),
            "old_size": 0,
            "new_size": current_files[path].get("size", 0),
        })

    # Common paths — check hash
    for path in sorted(baseline_keys & current_keys):
        b = baseline_files[path]
        c = current_files[path]
        entry = {
            "path":     path,
            "severity": c.get("severity", "MEDIUM"),
            "old_hash": b.get("hash", ""),
            "new_hash": c.get("hash", ""),
            "old_size": b.get("size", 0),
            "new_size": c.get("size", 0),
        }
        if b.get("hash") == c.get("hash"):
            entry["status"] = "Unchanged"
            unchanged.append(entry)
        else:
            entry["status"] = "Modified"
            modified.append(entry)

    return {
        "unchanged": unchanged,
        "modified":  modified,
        "deleted":   deleted,
        "new":       new_files,
        "summary": {
            "total":     len(unchanged) + len(modified) + len(deleted) + len(new_files),
            "unchanged": len(unchanged),
            "modified":  len(modified),
            "deleted":   len(deleted),
            "new":       len(new_files),
            "algorithm": algo,
            "elapsed_s": elapsed,
            "directory": directory,
            "baseline":  baseline_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    }
