"""Batch processor for JSX screen definition extraction.

Recursively walks a directory tree and parses every .jsx / .tsx file,
returning a combined JSON structure.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, List

from .jsx_parser import parse_jsx_file


# ───────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────

DEFAULT_EXCLUDE_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    "dist", "build", ".next", "coverage",
}

SUPPORTED_EXT = {".jsx", ".tsx"}


# ───────────────────────────────────────────────
# Batch parse
# ───────────────────────────────────────────────

def parse_directory(
    root_dir: str,
    exclude_dirs: set[str] | None = None,
) -> dict[str, Any]:
    """Recursively parse all JSX/TSX files under *root_dir*.

    Returns
    -------
    dict
        {
          "root": str,
          "files": [
            {
              "file": str,
              "elements": [ ...UIElement dicts... ]
            },
            ...
          ],
          "total_elements": int,
        }
    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    file_results: List[dict] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SUPPORTED_EXT:
                continue

            fpath = os.path.join(dirpath, fname)
            try:
                elements = parse_jsx_file(fpath)
                file_results.append({
                    "file": fpath,
                    "elements": [e.to_dict() for e in elements],
                })
            except Exception as exc:  # noqa: BLE001
                file_results.append({
                    "file": fpath,
                    "elements": [],
                    "error": str(exc),
                })

    total = sum(len(f["elements"]) for f in file_results)

    return {
        "root": root_dir,
        "files": file_results,
        "total_elements": total,
    }


# ───────────────────────────────────────────────
# CLI entry point
# ───────────────────────────────────────────────

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = parse_directory(target)
    print(json.dumps(result, ensure_ascii=False, indent=2))
