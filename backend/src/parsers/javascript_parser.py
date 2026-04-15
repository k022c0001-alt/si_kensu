"""JavaScript / JSX regex-based function call extractor."""

import re
from pathlib import Path
from typing import List

from .base import CallInfo

# Matches: identifier( or identifier.method(
_CALL_RE = re.compile(
    r"(?:(?P<obj>[A-Za-z_$][\w$]*)\.)?(?P<func>[A-Za-z_$][\w$]*)\s*\("
)
# Arrow / regular function declarations to detect current context
_FUNC_DECL_RE = re.compile(
    r"(?:function\s+(?P<name>[A-Za-z_$][\w$]*)\s*\()"
    r"|(?:const|let|var)\s+(?P<arrow>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("
    r"|(?:const|let|var)\s+(?P<arrow2>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?[A-Za-z_$][\w$]*\s*=>"
)
_CLASS_RE = re.compile(r"\bclass\s+(?P<name>[A-Za-z_$][\w$]*)")

# Keywords that are not real callees
_SKIP = frozenset(
    {
        "if", "for", "while", "switch", "catch", "function", "return",
        "typeof", "instanceof", "new", "delete", "void", "throw",
        "import", "export", "require", "class",
    }
)


class JavaScriptParser:
    """Parse JS/JSX source files and return CallInfo objects."""

    def parse_file(self, filepath: str) -> List[CallInfo]:
        path = Path(filepath)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        calls: List[CallInfo] = []
        current_class = ""
        current_func = ""

        for lineno, line in enumerate(source.splitlines(), start=1):
            # Update context
            m = _CLASS_RE.search(line)
            if m:
                current_class = m.group("name")

            m = _FUNC_DECL_RE.search(line)
            if m:
                name = m.group("name") or m.group("arrow") or m.group("arrow2")
                if name:
                    current_func = name

            caller = (
                f"{current_class}.{current_func}"
                if current_class and current_func
                else current_func or current_class or "<module>"
            )

            for m in _CALL_RE.finditer(line):
                func = m.group("func")
                obj = m.group("obj") or ""
                if func in _SKIP:
                    continue
                call = CallInfo(
                    caller=caller,
                    callee=obj,
                    function=func,
                    file=str(path),
                    line=lineno,
                )
                calls.append(call)

        return calls
