"""Python AST-based class/method extractor for Class diagram generation."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PropertyInfo:
    name: str
    type_hint: str = ""
    access: str = "public"  # public | private | protected


@dataclass
class MethodInfo:
    name: str
    params: List[str] = field(default_factory=list)
    return_type: str = ""
    access: str = "public"


@dataclass
class ClassInfo:
    name: str
    file: str
    bases: List[str] = field(default_factory=list)
    properties: List[PropertyInfo] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    language: str = "python"

    def get_access(self, name: str) -> str:
        if name.startswith("__") and not name.endswith("__"):
            return "private"
        if name.startswith("_"):
            return "protected"
        return "public"


def parse_python_file(filepath: str) -> List[ClassInfo]:
    """Extract all class definitions from a Python source file."""
    path = Path(filepath)
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []

    visitor = _ClassVisitor(str(path))
    visitor.visit(tree)
    return visitor.classes


class _ClassVisitor(ast.NodeVisitor):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.classes: List[ClassInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [self._name(b) for b in node.bases if self._name(b)]
        info = ClassInfo(name=node.name, file=self.filepath, bases=bases)

        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                if item in ast.walk(node):
                    method = self._extract_method(item, info)
                    info.methods.append(method)

                    if item.name == "__init__":
                        for stmt in ast.walk(item):
                            if (
                                isinstance(stmt, ast.Assign)
                                and len(stmt.targets) == 1
                            ):
                                t = stmt.targets[0]
                                if (
                                    isinstance(t, ast.Attribute)
                                    and isinstance(t.value, ast.Name)
                                    and t.value.id == "self"
                                ):
                                    prop = PropertyInfo(
                                        name=t.attr,
                                        access=info.get_access(t.attr),
                                    )
                                    if prop.name not in {p.name for p in info.properties}:
                                        info.properties.append(prop)
                            elif isinstance(stmt, ast.AnnAssign):
                                t = stmt.target
                                if (
                                    isinstance(t, ast.Attribute)
                                    and isinstance(t.value, ast.Name)
                                    and t.value.id == "self"
                                ):
                                    prop = PropertyInfo(
                                        name=t.attr,
                                        type_hint=self._annotation(stmt.annotation),
                                        access=info.get_access(t.attr),
                                    )
                                    if prop.name not in {p.name for p in info.properties}:
                                        info.properties.append(prop)

        self.classes.append(info)

    def _extract_method(
        self,
        node: ast.FunctionDef,
        owner: ClassInfo,
    ) -> MethodInfo:
        params = [a.arg for a in node.args.args if a.arg != "self"]
        ret = ""
        if node.returns:
            ret = self._annotation(node.returns)
        return MethodInfo(
            name=node.name,
            params=params,
            return_type=ret,
            access=owner.get_access(node.name),
        )

    @staticmethod
    def _name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""

    @staticmethod
    def _annotation(node: Optional[ast.expr]) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Subscript):
            return ast.unparse(node) if hasattr(ast, "unparse") else ""
        return ""
