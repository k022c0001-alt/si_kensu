"""
test_filter.py
フィルタエンジン (sequence/filter.py) のユニットテスト
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.sequence.filter import apply_filter


def _make_calls(*items):
    """テスト用の calls リストを生成するヘルパー"""
    result = []
    for item in items:
        result.append({
            "caller_file":   item.get("caller_file", "app"),
            "caller_func":   item.get("caller_func", "main"),
            "callee_object": item.get("callee_object", "service"),
            "callee_func":   item.get("callee_func", "do_something"),
            "line":          item.get("line", 1),
            "layer":         item.get("layer", "unknown"),
            "note":          item.get("note"),
        })
    return result


class TestDetailMode:
    def test_all_calls_returned(self):
        """detail モードでは全呼び出しが返る（ビルトイン除外以外）"""
        calls = _make_calls(
            {"callee_func": "get_user", "layer": "api"},
            {"callee_func": "save",     "layer": "db"},
        )
        result = apply_filter(calls, mode="detail", deduplicate=False)
        assert len(result) == 2

    def test_dunder_excluded(self):
        """__init__ などのマジックメソッドはデフォルトで除外される"""
        calls = _make_calls(
            {"callee_func": "__init__"},
            {"callee_func": "real_func"},
        )
        result = apply_filter(calls, mode="detail", deduplicate=False)
        funcs = [c["callee_func"] for c in result]
        assert "__init__" not in funcs
        assert "real_func" in funcs


class TestSummaryMode:
    def test_same_layer_excluded(self):
        """summary モードでは同一レイヤー同士の呼び出しが除外される"""
        calls = _make_calls(
            {"caller_file": "view", "callee_func": "render",   "layer": "ui"},
            {"caller_file": "api",  "callee_func": "fetch",    "layer": "api"},
        )
        # view (ui) -> render (ui) は除外される想定
        result = apply_filter(calls, mode="summary", deduplicate=False)
        # 少なくとも fetch (api) は残る
        funcs = [c["callee_func"] for c in result]
        assert "fetch" in funcs


class TestCustomMode:
    def test_include_layers_filters(self):
        """custom モードで include_layers を指定するとそれ以外が除外される"""
        calls = _make_calls(
            {"callee_func": "get_user", "layer": "api"},
            {"callee_func": "render",   "layer": "ui"},
            {"callee_func": "save",     "layer": "db"},
        )
        result = apply_filter(
            calls, mode="custom", include_layers=["api", "db"], deduplicate=False
        )
        layers = [c["layer"] for c in result]
        assert "ui" not in layers
        assert "api" in layers
        assert "db" in layers

    def test_exclude_funcs(self):
        """custom モードで exclude_funcs パターンに一致する関数が除外される"""
        calls = _make_calls(
            {"callee_func": "debug_log"},
            {"callee_func": "fetch_data"},
        )
        result = apply_filter(
            calls, mode="custom", exclude_funcs=[r"^debug_"], deduplicate=False
        )
        funcs = [c["callee_func"] for c in result]
        assert "debug_log" not in funcs
        assert "fetch_data" in funcs


class TestDeduplicate:
    def test_duplicate_pairs_removed(self):
        """同一 (callee_object, callee_func) ペアの重複が除去される"""
        calls = _make_calls(
            {"callee_object": "db", "callee_func": "query"},
            {"callee_object": "db", "callee_func": "query"},
            {"callee_object": "db", "callee_func": "query"},
        )
        result = apply_filter(calls, mode="detail", deduplicate=True)
        assert len(result) == 1

    def test_no_dedup_keeps_all(self):
        """deduplicate=False では重複を保持する"""
        calls = _make_calls(
            {"callee_object": "db", "callee_func": "query"},
            {"callee_object": "db", "callee_func": "query"},
        )
        result = apply_filter(calls, mode="detail", deduplicate=False)
        assert len(result) == 2
