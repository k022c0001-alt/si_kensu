"""CLI entry point for the Sequence diagram engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .sequence.analyzer import SequenceAnalyzer
from .sequence.filter import SequenceFilter
from .output.exporter import SequenceExporter


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="si_kensu",
        description="Analyse source code and generate Sequence diagrams.",
    )
    p.add_argument("root", help="Root directory to analyse")
    p.add_argument(
        "--mode",
        choices=["detail", "summary", "custom"],
        default="detail",
        help="Filter mode (default: detail)",
    )
    p.add_argument(
        "--include-layers",
        nargs="*",
        metavar="LAYER",
        help="Layer whitelist for custom mode (UI API DB Util App)",
    )
    p.add_argument(
        "--exclude-layers",
        nargs="*",
        metavar="LAYER",
        help="Layer blacklist for custom mode",
    )
    p.add_argument(
        "--format",
        choices=["json", "mermaid"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    p.add_argument("--output", "-o", help="Output file path (default: stdout)")
    p.add_argument(
        "--no-dedup",
        action="store_true",
        help="Disable deduplication of identical calls",
    )
    return p


def main(argv=None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    analyzer = SequenceAnalyzer()
    seq_filter = SequenceFilter()
    exporter = SequenceExporter()

    data = analyzer.analyze(args.root)

    filtered = seq_filter.filter(
        data,
        mode=args.mode,
        include_layers=args.include_layers,
        exclude_layers=args.exclude_layers,
        deduplicate=not args.no_dedup,
    )

    if args.format == "json":
        output = exporter.to_json(filtered)
    else:
        output = exporter.to_mermaid(filtered)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote output to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
