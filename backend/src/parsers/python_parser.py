"""Python AST-based function call extractor."""

import ast
from pathlib import Path
from typing import List

from .base import CallInfo


class PythonParser:
    """Parse Python source files and extract function call information."""

    def parse_file(self, filepath: str) -> List[CallInfo]:
        """Parse a single Python file and return its CallInfo list."""
        path = Path(filepath)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return []

        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            return []

        visitor = _CallVisitor(str(path))
        visitor.visit(tree)
        return visitor.calls


class _CallVisitor(ast.NodeVisitor):
    """AST visitor that collects function call sites."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.calls: List[CallInfo] = []
        self._current_class: List[str] = []
        self._current_func: List[str] = []

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #

    def _caller_name(self) -> str:
        parts = self._current_class + self._current_func
        return ".".join(parts) if parts else "<module>"

    @staticmethod
    def _callee_name(node: ast.Call) -> str:
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            obj = _CallVisitor._obj_name(func.value)
            return f"{obj}.{func.attr}" if obj else func.attr
        return "<unknown>"

    @staticmethod
    def _obj_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = _CallVisitor._obj_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return ""

    # ------------------------------------------------------------------ #
    # visitors
    # ------------------------------------------------------------------ #

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._current_class.append(node.name)
        self.generic_visit(node)
        self._current_class.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._current_func.append(node.name)
        self.generic_visit(node)
        self._current_func.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        callee_full = self._callee_name(node)
        parts = callee_full.rsplit(".", 1)
        callee_obj = parts[0] if len(parts) == 2 else ""
        function = parts[-1]

        call = CallInfo(
            caller=self._caller_name(),
            callee=callee_obj,
            function=function,
            file=self.filepath,
            line=node.lineno,
        )
        self.calls.append(call)
        self.generic_visit(node)
