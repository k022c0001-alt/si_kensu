"""Electron IPC handler for the Screen Definition engine.

Reads a newline-delimited JSON request from stdin and writes a JSON
response to stdout.  Supported actions:

* ``"parse_directory"``  – analyse every JSX/TSX file under *root*.
* ``"parse_file"``       – analyse a single JSX/TSX file.
* ``"export_json"``      – same as parse_directory but returns pretty JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ..parser.jsx_parser import parse_jsx_file
from ..parser.jsx_parser_batch import parse_directory
from ..filter.filter_rules import apply_all


# ───────────────────────────────────────────────
# Request handler
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
                from ..parser.jsx_parser import UIElement, ElementType
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

def _dict_to_uielement(d: dict):
    """Re-hydrate a UIElement from its to_dict() representation."""
    from ..parser.jsx_parser import UIElement, ElementType
    elem = UIElement(
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
    return elem


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
    ipc_stdio_loop()
