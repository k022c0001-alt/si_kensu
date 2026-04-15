"""
python_parser.py
Python ソースファイルを AST で解析し、関数呼び出しを抽出する
"""

import ast
from pathlib import Path
from typing import Optional

from .base import CallInfo
from ..layer.classifier import classify_layer


class PythonCallVisitor(ast.NodeVisitor):
    """
    ASTを走査して関数呼び出しを収集する。
    呼び出し元関数スコープを追跡するため、FunctionDef に入るたびに
    スタックを push / pop する。
    """

    def __init__(self, filename: str, source_lines: list):
        self.filename = Path(filename).stem
        self.source_lines = source_lines
        self.calls: list = []
        self._func_stack: list = []

    # ── スコープ追跡 ──────────────────────────
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._func_stack.append(node.name)
        self.generic_visit(node)
        self._func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    # ── 呼び出し抽出 ─────────────────────────
    def visit_Call(self, node: ast.Call):
        caller_func = self._func_stack[-1] if self._func_stack else "__module__"
        callee_object = ""
        callee_func = ""

        # パターン 1: obj.method()  →  Attribute
        if isinstance(node.func, ast.Attribute):
            callee_func = node.func.attr
            if isinstance(node.func.value, ast.Name):
                callee_object = node.func.value.id
            elif isinstance(node.func.value, ast.Attribute):
                # 深いチェーン (a.b.c()) → 先頭だけ取る
                callee_object = node.func.value.attr
            else:
                callee_object = "?"

        # パターン 2: func()  →  Name
        elif isinstance(node.func, ast.Name):
            callee_object = self.filename   # 同ファイル内と推定
            callee_func   = node.func.id

        else:
            self.generic_visit(node)
            return

        # 直前行からコメントを取得
        note = self._extract_preceding_comment(node.lineno)

        layer = classify_layer(self.filename, callee_func)

        self.calls.append(CallInfo(
            caller_file   = self.filename,
            caller_func   = caller_func,
            callee_object = callee_object,
            callee_func   = callee_func,
            line          = node.lineno,
            layer         = layer,
            note          = note,
        ))
        self.generic_visit(node)

    def _extract_preceding_comment(self, lineno: int) -> Optional[str]:
        """lineno の直前行（1つ上）が # コメントなら内容を返す"""
        idx = lineno - 2   # 0-indexed
        if 0 <= idx < len(self.source_lines):
            stripped = self.source_lines[idx].strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
        return None


def parse_python_file(filepath: str) -> list:
    """Python ファイルを AST 解析して CallInfo のリストを返す"""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    lines = source.splitlines()
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"[SKIP] SyntaxError in {filepath}: {e}")
        return []
    visitor = PythonCallVisitor(filepath, lines)
    visitor.visit(tree)
    return visitor.calls
