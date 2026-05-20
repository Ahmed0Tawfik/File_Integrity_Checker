import json
import os
import time
from pathlib import Path


def save_baseline(scan_result: dict, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        json.dump(scan_result, f, indent=2)

    return str(out.resolve())


def load_baseline(baseline_path: str) -> dict:
    path = Path(baseline_path)
    if not path.exists():
        raise FileNotFoundError(f"Baseline not found: '{baseline_path}'")

    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Baseline file is corrupted or not valid JSON: {e}")


def list_baselines(baselines_dir: str = "baselines") -> list:
    bd = Path(baselines_dir)
    if not bd.exists():
        return []

    results = []
    for f in sorted(bd.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = load_baseline(str(f))
            meta = data.get("__meta__", {})
        except Exception:
            meta = {}

        stat = f.stat()
        results.append({
            "path":       str(f.resolve()),
            "name":       f.name,
            "size_kb":    round(stat.st_size / 1024, 2),
            "modified":   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
            "algorithm":  meta.get("algorithm", "unknown"),
            "file_count": meta.get("file_count", "?"),
            "root":       meta.get("root", "?"),
            "scanned_at": time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(meta.get("scanned_at", stat.st_mtime))
            ),
        })
    return results
