"""React / JS component extractor using regular expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class PropInfo:
    name: str
    type_hint: str = ""
    required: bool = False


@dataclass
class HookInfo:
    name: str
    state_var: str = ""


@dataclass
class ComponentInfo:
    name: str
    file: str
    props: List[PropInfo] = field(default_factory=list)
    hooks: List[HookInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    language: str = "javascript"


# ------------------------------------------------------------------ #
# Regex patterns
# ------------------------------------------------------------------ #

_COMPONENT_FC = re.compile(
    r"(?:export\s+(?:default\s+)?)?(?:const|function)\s+(?P<name>[A-Z][A-Za-z0-9_]*)"
    r"\s*(?::\s*(?:React\.)?FC[^=]*?)?\s*[=(]"
)
_CLASS_COMPONENT = re.compile(
    r"class\s+(?P<name>[A-Z][A-Za-z0-9_]*)\s+extends\s+(?:React\.)?(?:Component|PureComponent)"
)
_PROPS_INTERFACE = re.compile(
    r"(?:interface|type)\s+(?P<name>[A-Za-z0-9_]*Props)\s*[={]"
)
_PROP_FIELD = re.compile(r"(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\??\s*:\s*(?P<type>[^;,\n]+)")
_USE_STATE = re.compile(
    r"const\s+\[(?P<var>[a-zA-Z_][a-zA-Z0-9_]*)[^\]]*\]\s*=\s*useState"
)
_CUSTOM_HOOK = re.compile(r"\buse(?P<name>[A-Z][A-Za-z0-9_]*)\s*\(")
_IMPORT_RE = re.compile(r"import\s+.*?\s+from\s+['\"](?P<src>[^'\"]+)['\"]")


def parse_js_file(filepath: str) -> List[ComponentInfo]:
    """Extract React components from a JS/JSX/TS/TSX file."""
    path = Path(filepath)
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    components: List[ComponentInfo] = []

    # Collect all component names first
    names = [m.group("name") for m in _COMPONENT_FC.finditer(source)]
    names += [m.group("name") for m in _CLASS_COMPONENT.finditer(source)]

    for name in names:
        comp = ComponentInfo(name=name, file=str(path))

        # Imports
        for m in _IMPORT_RE.finditer(source):
            comp.imports.append(m.group("src"))

        # useState hooks
        for m in _USE_STATE.finditer(source):
            comp.hooks.append(HookInfo(name="useState", state_var=m.group("var")))

        # Custom hooks
        for m in _CUSTOM_HOOK.finditer(source):
            hook_name = "use" + m.group("name")
            if not any(h.name == hook_name for h in comp.hooks):
                comp.hooks.append(HookInfo(name=hook_name))

        # Props (look for XxxProps interface / type)
        props_pattern = re.compile(
            rf"(?:interface|type)\s+{re.escape(name)}Props\s*[={{]([^}}]*)",
            re.DOTALL,
        )
        pm = props_pattern.search(source)
        if pm:
            block = pm.group(1)
            for fm in _PROP_FIELD.finditer(block):
                comp.props.append(
                    PropInfo(
                        name=fm.group("name"),
                        type_hint=fm.group("type").strip(),
                    )
                )

        components.append(comp)

    return components
