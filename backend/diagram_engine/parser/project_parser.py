"""Project-level parser: integrates multiple files into a dependency graph."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .py_parser import ClassInfo, parse_python_file
from .js_parser import ComponentInfo, parse_js_file

_SKIP_DIRS = frozenset(
    {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
)

_IMPORT_RE = re.compile(
    r"(?:from\s+['\"](?P<py_from>[^'\"]+)['\"])"
    r"|(?:import\s+.*?from\s+['\"](?P<js_from>[^'\"]+)['\"])"
    r"|(?:require\s*\(\s*['\"](?P<req>[^'\"]+)['\"]\s*\))",
    re.MULTILINE,
)


@dataclass
class ProjectData:
    """Holds all parsed class/component info and the dependency graph."""

    classes: List[ClassInfo] = field(default_factory=list)
    components: List[ComponentInfo] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classes": [
                {
                    "name": c.name,
                    "file": c.file,
                    "language": c.language,
                    "bases": c.bases,
                    "properties": [
                        {
                            "name": p.name,
                            "type": p.type_hint,
                            "access": p.access,
                        }
                        for p in c.properties
                    ],
                    "methods": [
                        {
                            "name": m.name,
                            "params": m.params,
                            "return": m.return_type,
                            "access": m.access,
                        }
                        for m in c.methods
                    ],
                }
                for c in self.classes
            ],
            "components": [
                {
                    "name": c.name,
                    "file": c.file,
                    "language": c.language,
                    "props": [
                        {"name": p.name, "type": p.type_hint}
                        for p in c.props
                    ],
                    "hooks": [h.name for h in c.hooks],
                    "imports": c.imports,
                }
                for c in self.components
            ],
            "dependencies": self.dependencies,
            "errors": self.errors,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class ProjectParser:
    """Walk a source tree and produce a :class:`ProjectData` instance."""

    def parse(self, root: str) -> ProjectData:
        data = ProjectData()
        root_path = Path(root)
        if not root_path.exists():
            data.errors.append(f"Directory not found: {root}")
            return data

        for filepath in self._walk(root_path):
            suffix = filepath.suffix.lower()
            try:
                if suffix == ".py":
                    classes = parse_python_file(str(filepath))
                    data.classes.extend(classes)
                    self._add_py_deps(filepath, data)
                elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
                    components = parse_js_file(str(filepath))
                    data.components.extend(components)
                    self._add_js_deps(filepath, data)
            except Exception as exc:
                data.errors.append(f"{filepath}: {exc}")

        return data

    # ------------------------------------------------------------------ #

    def _add_py_deps(self, filepath: Path, data: ProjectData) -> None:
        try:
            source = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        key = str(filepath)
        deps: List[str] = []
        for line in source.splitlines():
            m = re.match(r"^from\s+([\w.]+)\s+import", line)
            if m:
                deps.append(m.group(1))
            m2 = re.match(r"^import\s+([\w., ]+)", line)
            if m2:
                for part in m2.group(1).split(","):
                    deps.append(part.strip().split(" ")[0])
        if deps:
            data.dependencies[key] = deps

    def _add_js_deps(self, filepath: Path, data: ProjectData) -> None:
        try:
            source = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        key = str(filepath)
        deps: List[str] = []
        for m in _IMPORT_RE.finditer(source):
            src = m.group("js_from") or m.group("req")
            if src:
                deps.append(src)
        if deps:
            data.dependencies[key] = deps

    @staticmethod
    def _walk(root: Path):
        for item in root.iterdir():
            if item.is_dir():
                if item.name not in _SKIP_DIRS:
                    yield from ProjectParser._walk(item)
            elif item.is_file():
                yield item
