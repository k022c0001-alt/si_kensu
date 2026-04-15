"""
test_parser.py
Python / JavaScript パーサーのユニットテスト
"""

import textwrap
import tempfile
import os
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.parsers.python_parser import parse_python_file
from src.parsers.javascript_parser import parse_js_file


# ─────────────────────────────────────────────
# Python パーサー テスト
# ─────────────────────────────────────────────

def _write_tmp(suffix: str, content: str) -> str:
    """一時ファイルを作成してパスを返す"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content))
    return path


class TestPythonParser:
    def test_simple_call(self):
        """obj.method() 形式の呼び出しが抽出される"""
        code = """\
        def fetch_data():
            result = api.get_user(id=1)
        """
        path = _write_tmp(".py", code)
        try:
            calls = parse_python_file(path)
        finally:
            os.unlink(path)

        assert any(c.callee_func == "get_user" for c in calls)

    def test_plain_call(self):
        """func() 形式の呼び出しが抽出される"""
        code = """\
        def process():
            validate(data)
        """
        path = _write_tmp(".py", code)
        try:
            calls = parse_python_file(path)
        finally:
            os.unlink(path)

        assert any(c.callee_func == "validate" for c in calls)

    def test_caller_func_tracked(self):
        """呼び出し元関数名が正しく追跡される"""
        code = """\
        def my_func():
            helper()
        """
        path = _write_tmp(".py", code)
        try:
            calls = parse_python_file(path)
        finally:
            os.unlink(path)

        helper_calls = [c for c in calls if c.callee_func == "helper"]
        assert helper_calls
        assert helper_calls[0].caller_func == "my_func"

    def test_preceding_comment_extracted(self):
        """直前行の # コメントが note として取得される"""
        code = """\
        def run():
            # ユーザー取得
            api.get_user()
        """
        path = _write_tmp(".py", code)
        try:
            calls = parse_python_file(path)
        finally:
            os.unlink(path)

        notes = [c.note for c in calls if c.callee_func == "get_user"]
        assert notes and notes[0] == "ユーザー取得"

    def test_syntax_error_returns_empty(self):
        """構文エラーのファイルは空リストを返す（クラッシュしない）"""
        code = "def broken(:"
        path = _write_tmp(".py", code)
        try:
            calls = parse_python_file(path)
        finally:
            os.unlink(path)
        assert calls == []


# ─────────────────────────────────────────────
# JavaScript パーサー テスト
# ─────────────────────────────────────────────

class TestJavaScriptParser:
    def test_method_call(self):
        """obj.method() 形式の呼び出しが抽出される"""
        code = """\
        function loadUser() {
            api.fetchUser(id);
        }
        """
        path = _write_tmp(".js", code)
        try:
            calls = parse_js_file(path)
        finally:
            os.unlink(path)

        assert any(c.callee_func == "fetchUser" for c in calls)

    def test_builtin_excluded(self):
        """JS ビルトイン関数が除外される"""
        code = """\
        function run() {
            parseInt('42');
            isNaN(value);
            api.fetchUser(id);
        }
        """
        path = _write_tmp(".js", code)
        try:
            calls = parse_js_file(path)
        finally:
            os.unlink(path)

        funcs = [c.callee_func for c in calls]
        assert "parseInt" not in funcs     # JS_BUILTINS に含まれる
        assert "isNaN" not in funcs        # JS_BUILTINS に含まれる
        assert "fetchUser" in funcs        # 通常の呼び出しは残る

    def test_comment_extracted(self):
        """直前行の // コメントが note として取得される"""
        code = """\
        function run() {
            // データ保存
            db.save(record);
        }
        """
        path = _write_tmp(".js", code)
        try:
            calls = parse_js_file(path)
        finally:
            os.unlink(path)

        notes = [c.note for c in calls if c.callee_func == "save"]
        assert notes and notes[0] == "データ保存"
