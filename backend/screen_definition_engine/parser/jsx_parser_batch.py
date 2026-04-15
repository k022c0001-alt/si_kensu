"""Batch processor for JSX screen definition extraction.

Recursively walks a directory tree and parses every .jsx / .tsx / .js / .ts
file, returning a combined JSON structure.

Class-based API
---------------
    batch = BatchJSXParser()
    results = batch.parse_directory('frontend/src/components')
    batch.export_json('frontend/src/components', 'screen_definitions.json')

Functional API (retained for backwards compatibility)
------------------------------------------------------
    result = parse_directory('frontend/src/components')
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .jsx_parser import JSXParser, UIElement, parse_jsx_file


# ───────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────

DEFAULT_EXCLUDE_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    "dist", "build", ".next", "coverage",
}

SUPPORTED_EXT = {".jsx", ".tsx", ".js", ".ts"}


# ───────────────────────────────────────────────
# Class-based API
# ───────────────────────────────────────────────

class BatchJSXParser:
    """Batch processor that wraps :class:`JSXParser` for directory-wide parsing.

    Parameters
    ----------
    config : dict, optional
        Forwarded unchanged to the underlying :class:`JSXParser`.
    """

    SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".jsx", ".tsx", ".js", ".ts"})

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._parser = JSXParser(config)

    def parse_directory(
        self,
        directory: str,
        recursive: bool = True,
    ) -> Dict[str, List[dict]]:
        """Parse all supported files under *directory*.

        Parameters
        ----------
        directory : str
            Root directory to search.
        recursive : bool
            When *True* (default) recurse into sub-directories, skipping
            common non-source directories (node_modules, .git, etc.).

        Returns
        -------
        dict
            ``{ "<relative/path/to/file.jsx>": [ ...UIElement dicts... ] }``
        """
        root = Path(directory)
        results: Dict[str, List[dict]] = {}

        file_paths: List[Path] = (
            list(self._walk_recursive(root))
            if recursive
            else [
                p
                for p in root.iterdir()
                if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
        )

        for fpath in file_paths:
            try:
                rel = str(fpath.relative_to(root))
            except ValueError:
                rel = str(fpath)
            try:
                elements = self._parser.parse_file(str(fpath))
                results[rel] = [e.to_dict() for e in elements]
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[BatchJSXParser] Error parsing {fpath}: {exc}",
                    file=sys.stderr,
                )
                results[rel] = []

        return results

    def export_json(self, directory: str, output_file: str) -> None:
        """Parse *directory* and write the result as JSON to *output_file*.

        Parameters
        ----------
        directory : str
            Root directory to parse.
        output_file : str
            Destination JSON file path (parent directories are created
            automatically).
        """
        results = self.parse_directory(directory)
        output = Path(output_file)
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("w", encoding="utf-8") as fh:
                json.dump(results, fh, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(
                f"[BatchJSXParser] Failed to write {output_file}: {exc}",
                file=sys.stderr,
            )
            raise

    def _walk_recursive(self, root: Path):
        """Yield supported files, skipping common non-source directories."""
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS
            ]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    yield fpath


# ───────────────────────────────────────────────
# Functional API (backwards compatible)
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
