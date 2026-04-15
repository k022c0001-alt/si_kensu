"""Sequence diagram IPC stdio handler.

Called by the Electron main process when ``action == "sequence"``.
Reads a single JSON line from stdin and writes a JSON response to stdout.
"""

from __future__ import annotations

import json
import sys

from .sequence.analyzer import analyze_directory
from .sequence.filter import apply_filter
from .output.exporter import to_json_string, build_mermaid


def handle_request(request: dict) -> dict:
    root = request.get("root", ".")
    mode = request.get("mode", "detail")
    include_layers = request.get("includeLayers")
    exclude_funcs = request.get("excludeFuncs")
    fmt = request.get("format", "json")

    data = analyze_directory(root)
    filtered_calls = apply_filter(
        calls=data.calls,
        mode=mode,
        include_layers=include_layers,
        exclude_funcs=exclude_funcs,
    )

    if fmt == "mermaid":
        return {"mermaid": build_mermaid(data, filtered_calls)}
    return {"data": json.loads(to_json_string(data))}


def ipc_stdio_loop() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
        except Exception as exc:
            response = {"error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    ipc_stdio_loop()
