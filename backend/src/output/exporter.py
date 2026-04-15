"""
exporter.py
解析結果を JSON または Mermaid sequenceDiagram テキストに出力する
"""

import json
import re
from dataclasses import asdict

from ..parsers.base import SequenceData


# ─────────────────────────────────────────────
# JSON 出力
# ─────────────────────────────────────────────

def export_json(data: SequenceData, output_path: str) -> None:
    """SequenceData を JSON ファイルに書き出す"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(data), f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON saved to: {output_path}")


def to_json_string(data: SequenceData) -> str:
    """SequenceData を JSON 文字列として返す"""
    return json.dumps(asdict(data), ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# Mermaid sequenceDiagram 出力
# ─────────────────────────────────────────────

def build_mermaid(data: SequenceData, calls: list = None) -> str:
    """
    SequenceData（または絞り込み済み calls リスト）から
    Mermaid sequenceDiagram テキストを生成する。

    Args:
        data: SequenceData（participants 一覧に使用）
        calls: 出力対象の呼び出しリスト。None の場合は data.calls を使用。
    """
    if calls is None:
        calls = data.calls

    lines = ["sequenceDiagram"]

    # 参加者宣言
    for participant in data.participants:
        if participant and participant not in ("?", ""):
            lines.append(f"    participant {_safe_name(participant)}")

    lines.append("")

    # 呼び出し矢印
    for call in calls:
        caller = _safe_name(call.get("caller_file", "unknown"))
        callee = _safe_name(call.get("callee_object", "unknown"))
        func   = call.get("callee_func", "")
        note   = call.get("note")

        if note:
            lines.append(f"    Note over {caller},{callee}: {note}")

        lines.append(f"    {caller}->>{callee}: {func}()")

    return "\n".join(lines)


def export_mermaid(data: SequenceData, output_path: str, calls: list = None) -> None:
    """Mermaid テキストをファイルに書き出す"""
    text = build_mermaid(data, calls)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[OK] Mermaid saved to: {output_path}")


# ─────────────────────────────────────────────
# ユーティリティ
# ─────────────────────────────────────────────

def _safe_name(name: str) -> str:
    """Mermaid のラベルに使えない文字を除去する"""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)
