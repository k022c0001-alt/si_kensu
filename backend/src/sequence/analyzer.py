"""Sequence diagram analyzer: walk a directory tree and aggregate CallInfo."""

from pathlib import Path
from typing import List, Optional

from ..parsers.base import CallInfo, SequenceData
from ..parsers.python_parser import PythonParser
from ..parsers.javascript_parser import JavaScriptParser
from ..layer.classifier import classify_layer

_PY_PARSER = PythonParser()
_JS_PARSER = JavaScriptParser()

_SUFFIX_MAP = {
    ".py": _PY_PARSER,
    ".js": _JS_PARSER,
    ".jsx": _JS_PARSER,
    ".ts": _JS_PARSER,
    ".tsx": _JS_PARSER,
}

_SKIP_DIRS = frozenset(
    {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
)


class SequenceAnalyzer:
    """Walk a source tree and produce a :class:`SequenceData` object."""

    def analyze(
        self,
        root: str,
        include_suffixes: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
    ) -> SequenceData:
        """Recursively parse *root* and return aggregated sequence data."""
        data = SequenceData()
        skip = _SKIP_DIRS | set(exclude_dirs or [])
        suffixes = set(include_suffixes) if include_suffixes else set(_SUFFIX_MAP.keys())

        root_path = Path(root)
        if not root_path.exists():
            data.add_error(f"Directory not found: {root}")
            return data

        for filepath in self._walk(root_path, skip):
            if filepath.suffix not in suffixes:
                continue
            parser = _SUFFIX_MAP.get(filepath.suffix)
            if parser is None:
                continue

            try:
                calls: List[CallInfo] = parser.parse_file(str(filepath))
            except Exception as exc:
                data.add_error(f"{filepath}: {exc}")
                continue

            data.add_file(str(filepath))
            for call in calls:
                call.layer_caller = classify_layer(call.caller, call.file)
                call.layer_callee = classify_layer(call.callee, call.file)
                data.add_call(call)

        return data

    # ------------------------------------------------------------------ #

    @staticmethod
    def _walk(root: Path, skip: frozenset):
        for item in root.iterdir():
            if item.is_dir():
                if item.name not in skip:
                    yield from SequenceAnalyzer._walk(item, skip)
            elif item.is_file():
                yield item
