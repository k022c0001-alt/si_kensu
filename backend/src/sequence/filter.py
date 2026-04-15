"""
filter.py
抽出済み呼び出しデータにルールを適用してシーケンスを絞り込むフィルタエンジン。

モード:
  detail  – 全呼び出しをそのまま出力
  summary – 境界をまたぐ呼び出しのみ（異なるレイヤー間）
  custom  – exclude_funcs / include_layers を指定して細かく制御
"""

import re
from typing import Optional


# デフォルト除外関数名パターン（ノイズになりやすいもの）
DEFAULT_EXCLUDE_PATTERNS = [
    re.compile(r"^__\w+__$"),          # __init__, __repr__ など
    re.compile(r"^(print|len|str|int|float|bool|list|dict|set|tuple)$"),
]


def _matches_any(name: str, patterns: list) -> bool:
    return any(p.search(name) for p in patterns)


def apply_filter(
    calls: list,
    mode: str = "detail",
    include_layers: Optional[list] = None,
    exclude_funcs: Optional[list] = None,
    deduplicate: bool = True,
) -> list:
    """
    calls: SequenceData.calls (list of dict)
    mode:
        "detail"  – 全呼び出しを出力（デフォルト除外パターンのみ適用）
        "summary" – 異なるレイヤー間の呼び出しのみ
        "custom"  – include_layers / exclude_funcs を使った細かい制御
    include_layers: 含めるレイヤーのリスト（custom モード用）
    exclude_funcs:  除外する関数名の正規表現リスト（custom モード用）
    deduplicate:    同一 (callee_object, callee_func) の連続重複を除去

    Returns:
        フィルタ済みの calls リスト
    """
    result = []
    exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    if exclude_funcs:
        exclude_patterns.extend(re.compile(p) for p in exclude_funcs)

    seen_pairs: set = set()

    for call in calls:
        callee_func = call.get("callee_func", "")
        layer = call.get("layer", "unknown")

        # デフォルト除外
        if _matches_any(callee_func, exclude_patterns):
            continue

        # モード別フィルタ
        if mode == "summary":
            # 同一レイヤー内の呼び出しは除外
            caller_layer = _infer_caller_layer(call, calls)
            if caller_layer == layer:
                continue

        elif mode == "custom":
            # レイヤーフィルタ
            if include_layers and layer not in include_layers:
                continue

        # 重複除去（同一ペア）
        if deduplicate:
            pair = (call.get("callee_object"), callee_func)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

        result.append(call)

    return result


def _infer_caller_layer(call: dict, all_calls: list) -> str:
    """
    caller_file / caller_func からレイヤーを推定する。
    同一ファイルの他の呼び出しレイヤー情報を参照するシンプルな近似。
    """
    caller_file = call.get("caller_file", "")
    caller_func = call.get("caller_func", "")

    for c in all_calls:
        if c.get("caller_file") == caller_file and c.get("callee_func") == caller_func:
            return c.get("layer", "unknown")
    return "unknown"
