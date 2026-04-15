"""Electron IPC entry point and CLI for the Class diagram engine."""

from __future__ import annotations

import argparse
import json
import sys

from ..parser.project_parser import ProjectParser
from ..filter.filter_engine import ClassDiagramFilter, to_mermaid_class_diagram


def handle_ipc(request: dict) -> dict:
    """Process an IPC request from Electron and return a response dict.

    Expected request keys
    ---------------------
    action : str
        ``"parse"``     – parse a project directory.
        ``"mermaid"``   – parse + generate Mermaid output.
    root   : str        – root directory to analyse.
    mode   : str        – ``"detail"`` | ``"overview"`` (default: ``"detail"``).
    languages : list    – optional language filter, e.g. ``["python"]``.
    """
    action = request.get("action", "parse")
    root = request.get("root", ".")
    mode = request.get("mode", "detail")
    languages = request.get("languages")

    parser = ProjectParser()
    filt = ClassDiagramFilter()

    data = parser.parse(root)
    filtered = filt.filter(data, mode=mode, languages=languages)

    if action == "mermaid":
        return {"mermaid": to_mermaid_class_diagram(filtered)}

    return {"data": filtered.to_dict()}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="si_kensu_class",
        description="Analyse source code and generate Class diagrams.",
    )
    p.add_argument("root", help="Root directory to analyse")
    p.add_argument(
        "--mode",
        choices=["detail", "overview"],
        default="detail",
        help="Filter mode (default: detail)",
    )
    p.add_argument(
        "--languages",
        nargs="*",
        metavar="LANG",
        help="Language filter (python / javascript)",
    )
    p.add_argument(
        "--format",
        choices=["json", "mermaid"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    p.add_argument("--output", "-o", help="Output file path (default: stdout)")
    return p


def main(argv=None) -> None:
    args = _build_parser().parse_args(argv)

    response = handle_ipc(
        {
            "action": "mermaid" if args.format == "mermaid" else "parse",
            "root": args.root,
            "mode": args.mode,
            "languages": args.languages,
        }
    )

    if args.format == "mermaid":
        output = response.get("mermaid", "")
    else:
        output = json.dumps(response.get("data", {}), ensure_ascii=False, indent=2)

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote output to {args.output}", file=sys.stderr)
    else:
        print(output)


# Support invocation via Electron: read JSON from stdin, write JSON to stdout.
def ipc_stdio_loop() -> None:
    """Read newline-delimited JSON from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_ipc(request)
        except Exception as exc:
            response = {"error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments: assume IPC stdio mode
        ipc_stdio_loop()
    else:
        main()
