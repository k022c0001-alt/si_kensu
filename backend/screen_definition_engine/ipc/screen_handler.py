"""Electron IPC handler for the Screen Definition engine.

Reads a newline-delimited JSON request from stdin and writes a JSON
response to stdout.  Supported actions:

* ``"parse_directory"``  – analyse every JSX/TSX file under *root*.
* ``"parse_file"``       – analyse a single JSX/TSX file.
* ``"export_json"``      – same as parse_directory but returns pretty JSON.

CLI usage (invoked by Electron ipcMain via spawn):
    python screen_handler.py '{"root":"./src","filter":{"mode":"strict"}}'
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

# Allow imports when invoked directly as a script (sys.argv[0] == screen_handler.py)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from ..parser.jsx_parser import parse_jsx_file, UIElement, ElementType
    from ..parser.jsx_parser_batch import BatchJSXParser, parse_directory
    from ..filter.filter_rules import FilterRuleSet, apply_all
except ImportError:
    # Running as a script directly
    from screen_definition_engine.parser.jsx_parser import parse_jsx_file, UIElement, ElementType  # type: ignore
    from screen_definition_engine.parser.jsx_parser_batch import BatchJSXParser, parse_directory  # type: ignore
    from screen_definition_engine.filter.filter_rules import FilterRuleSet, apply_all  # type: ignore


# ───────────────────────────────────────────────
# Request handler (stdio IPC)
# ───────────────────────────────────────────────

def handle_request(request: dict) -> dict:
    """Process one IPC request and return a response dict.

    Parameters
    ----------
    request : dict
        ``action``  – one of ``"parse_directory"`` | ``"parse_file"`` |
                      ``"export_json"``.
        ``root``    – directory path (for directory actions).
        ``file``    – file path (for ``"parse_file"``).
        ``filter``  – ``true`` (default) to apply default filter rules.
    """
    action = request.get("action", "parse_directory")
    apply_filter: bool = request.get("filter", True)

    if action in ("parse_directory", "export_json"):
        root = request.get("root", ".")
        data = parse_directory(root)

        if apply_filter:
            for file_entry in data["files"]:
                raw_elems = [
                    _dict_to_uielement(e) for e in file_entry["elements"]
                ]
                filtered = apply_all(raw_elems)
                file_entry["elements"] = [e.to_dict() for e in filtered]
            data["total_elements"] = sum(
                len(f["elements"]) for f in data["files"]
            )

        return {"data": data}

    if action == "parse_file":
        filepath = request.get("file", "")
        if not filepath:
            return {"error": "Missing 'file' key in request"}

        elements = parse_jsx_file(filepath)
        if apply_filter:
            elements = apply_all(elements)

        return {
            "data": {
                "file": filepath,
                "elements": [e.to_dict() for e in elements],
            }
        }

    return {"error": f"Unknown action: {action}"}


# ───────────────────────────────────────────────
# Helper
# ───────────────────────────────────────────────

def _dict_to_uielement(d: dict) -> UIElement:
    """Re-hydrate a UIElement from its to_dict() representation."""
    return UIElement(
        element_id=d.get("element_id", ""),
        name=d.get("name", ""),
        type=d.get("type", ""),
        component_type=ElementType(d.get("component_type", "unknown")),
        required=d.get("required", False),
        max_length=d.get("max_length"),
        placeholder=d.get("placeholder", ""),
        default_value=d.get("default_value", ""),
        event_handlers=d.get("event_handlers", {}),
        comment=d.get("comment", ""),
        line_number=d.get("line_number", 0),
    )


# ───────────────────────────────────────────────
# CLI main() – invoked by Electron ipcMain spawn
# ───────────────────────────────────────────────

def main() -> None:
    """Entry point when invoked as ``python screen_handler.py '<json>'``.

    Reads a JSON config from ``sys.argv[1]``, parses the target directory,
    applies filter rules, computes statistics, and prints a JSON response
    to stdout.  All warnings/errors go to stderr so stdout stays clean JSON.
    """
    if len(sys.argv) < 2:
        output = {
            "success": False,
            "error": "Usage: screen_handler.py '<json_config>'",
        }
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)

    # ── Parse parameters ──────────────────────────
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        output = {"success": False, "error": f"JSON Parse Error: {e}"}
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)

    # ── Main processing ───────────────────────────
    try:
        root = params.get("root", ".")
        filter_config = params.get("filter", {})
        extract_comments = params.get("extract_comments", True)
        filter_mode = filter_config.get("mode", "normal") if isinstance(filter_config, dict) else "normal"

        project_root = str(Path(root).resolve())

        batch_parser = BatchJSXParser()
        raw_results = batch_parser.parse_directory(root)

        # Reconstruct UIElement objects for filtering
        rule_set = FilterRuleSet(mode=filter_mode)

        files_output: dict[str, list] = {}
        total_elements = 0
        filtered_elements = 0
        by_type: dict[str, int] = {}

        for rel_path, elem_dicts in raw_results.items():
            elements = [_dict_to_uielement(e) for e in elem_dicts]
            total_elements += len(elements)

            filtered = rule_set.apply_all(elements)
            filtered_elements += len(filtered)

            for elem in filtered:
                ct = elem.component_type.value if hasattr(elem.component_type, "value") else str(elem.component_type)
                by_type[ct] = by_type.get(ct, 0) + 1

            files_output[rel_path] = [e.to_dict() for e in filtered]

        output = {
            "success": True,
            "project_root": project_root,
            "files": files_output,
            "stats": {
                "total_files": len(raw_results),
                "total_elements": total_elements,
                "filtered_elements": filtered_elements,
                "by_type": by_type,
            },
        }
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        output = {
            "success": False,
            "error": str(e),
            "details": traceback.format_exc(),
        }
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)


# ───────────────────────────────────────────────
# IPC stdio loop
# ───────────────────────────────────────────────

def ipc_stdio_loop() -> None:
    """Read newline-delimited JSON from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
        except Exception as exc:  # noqa: BLE001
            response = {"error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
