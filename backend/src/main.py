"""
main.py
CLI エントリーポイント

使用例:
  python -m src.main <target_dir> [output_file] [--mode detail|summary|custom] [--format json|mermaid]
"""

import sys
import argparse

from .sequence.analyzer import analyze_directory
from .sequence.filter import apply_filter
from .output.exporter import export_json, export_mermaid


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="ソースコードを解析してシーケンス図を生成します"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="解析対象のディレクトリ（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="sequence_data.json",
        help="出力ファイルパス（デフォルト: sequence_data.json）",
    )
    parser.add_argument(
        "--mode",
        choices=["detail", "summary", "custom"],
        default="detail",
        help="フィルタモード（デフォルト: detail）",
    )
    parser.add_argument(
        "--format",
        choices=["json", "mermaid"],
        default="json",
        help="出力フォーマット（デフォルト: json）",
    )
    parser.add_argument(
        "--include-layers",
        nargs="+",
        metavar="LAYER",
        help="custom モード: 含めるレイヤー名（例: api db）",
    )
    parser.add_argument(
        "--exclude-funcs",
        nargs="+",
        metavar="PATTERN",
        help="custom モード: 除外する関数名の正規表現パターン",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print(f"Scanning: {args.target}")
    data = analyze_directory(args.target)
    print(f"  {len(data.source_files)} files parsed, {len(data.calls)} calls found.")

    # フィルタ適用
    filtered_calls = apply_filter(
        calls          = data.calls,
        mode           = args.mode,
        include_layers = args.include_layers,
        exclude_funcs  = args.exclude_funcs,
    )
    print(f"  {len(filtered_calls)} calls after filter (mode={args.mode}).")

    # 出力
    if args.format == "mermaid":
        output = args.output
        if not output.endswith(".mmd"):
            output = output.rsplit(".", 1)[0] + ".mmd"
        export_mermaid(data, output, filtered_calls)
    else:
        export_json(data, args.output)


if __name__ == "__main__":
    main()
