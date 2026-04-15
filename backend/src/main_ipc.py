"""Sequence diagram IPC stdio handler.

Called by the Electron main process when ``action == "sequence"``.
Reads a single JSON line from stdin and writes a JSON response to stdout.
"""

from __future__ import annotations

import json
import sys

from .sequence.analyzer import SequenceAnalyzer
from .sequence.filter import SequenceFilter
from .output.exporter import SequenceExporter


def handle_request(request: dict) -> dict:
    root = request.get("root", ".")
    mode = request.get("mode", "detail")
    include_layers = request.get("includeLayers")
    exclude_layers = request.get("excludeLayers")
    fmt = request.get("format", "json")

    analyzer = SequenceAnalyzer()
    seq_filter = SequenceFilter()
    exporter = SequenceExporter()

    data = analyzer.analyze(root)
    filtered = seq_filter.filter(
        data,
        mode=mode,
        include_layers=include_layers,
        exclude_layers=exclude_layers,
    )

    if fmt == "mermaid":
        return {"mermaid": exporter.to_mermaid(filtered)}
    return {"data": json.loads(exporter.to_json(filtered))}


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
