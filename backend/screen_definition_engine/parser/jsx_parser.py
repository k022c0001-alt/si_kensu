"""JSX UI element extractor for screen definition generation.

Parses a single JSX/TSX file and returns a list of UIElement objects
describing every form element found in the source.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ───────────────────────────────────────────────
# Data model
# ───────────────────────────────────────────────

class ElementType(str, Enum):
    INPUT = "input"
    BUTTON = "button"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class UIElement:
    element_id: str = ""
    name: str = ""
    type: str = ""                             # HTML type attribute (text, email, …)
    component_type: ElementType = ElementType.UNKNOWN
    required: bool = False
    max_length: Optional[int] = None
    placeholder: str = ""
    default_value: str = ""
    event_handlers: Dict[str, str] = field(default_factory=dict)
    comment: str = ""
    line_number: int = 0

    def to_dict(self) -> dict:
        return {
            "element_id": self.element_id,
            "name": self.name,
            "type": self.type,
            "component_type": self.component_type.value,
            "required": self.required,
            "max_length": self.max_length,
            "placeholder": self.placeholder,
            "default_value": self.default_value,
            "event_handlers": self.event_handlers,
            "comment": self.comment,
            "line_number": self.line_number,
        }


# ───────────────────────────────────────────────
# Regex helpers
# ───────────────────────────────────────────────

# Match an opening JSX tag, possibly self-closing.
# Group "tag"  – tag name
# Group "attrs" – everything between < and > / />
_TAG_RE = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9._-]*)"
    r"(?P<attrs>[^>]*?)(?:/?>)",
    re.DOTALL,
)

# Match a single JSX attribute  name="value"  or  name={expr}  or bare  name
_ATTR_RE = re.compile(
    r'(?P<key>[A-Za-z_][A-Za-z0-9_-]*)'
    r'(?:\s*=\s*(?:"(?P<dq>[^"]*)"|\'(?P<sq>[^\']*)\'|\{(?P<expr>[^}]*)\}))?',
)

# Inline JSX comment preceding a tag  {/* … */}
_COMMENT_RE = re.compile(r'\{/\*(?P<text>.*?)\*/\}', re.DOTALL)

# HTML-style comment  <!-- … -->
_HTML_COMMENT_RE = re.compile(r'<!--(?P<text>.*?)-->', re.DOTALL)

# Custom PascalCase component names to treat as CUSTOM
_PASCAL_RE = re.compile(r'^[A-Z][A-Za-z0-9]*$')

# Known HTML form elements → ElementType mapping
_HTML_ELEMENTS: Dict[str, ElementType] = {
    "input": ElementType.INPUT,
    "button": ElementType.BUTTON,
    "select": ElementType.SELECT,
    "textarea": ElementType.TEXTAREA,
}


# ───────────────────────────────────────────────
# Attribute extraction
# ───────────────────────────────────────────────

def _attr_value(attr_match: re.Match) -> str:
    """Return the string value of an attribute match (double/single/expr)."""
    return (
        attr_match.group("dq")
        or attr_match.group("sq")
        or attr_match.group("expr")
        or ""
    )


def _parse_attrs(attrs_str: str) -> Dict[str, str]:
    """Extract all key/value pairs from a JSX attribute string."""
    result: Dict[str, str] = {}
    for m in _ATTR_RE.finditer(attrs_str):
        key = m.group("key")
        value = _attr_value(m)
        result[key] = value
    return result


def _extract_event_handlers(attrs: Dict[str, str]) -> Dict[str, str]:
    """Return attributes whose names start with 'on' (e.g. onClick)."""
    return {k: v for k, v in attrs.items() if k.startswith("on") and k[2:3].isupper()}


# ───────────────────────────────────────────────
# Comment extraction
# ───────────────────────────────────────────────

def _preceding_comment(source: str, pos: int) -> str:
    """Return the text of the nearest JSX or HTML comment before *pos*."""
    preceding = source[:pos]

    # Look for {/* … */} comment
    matches = list(_COMMENT_RE.finditer(preceding))
    if matches:
        last = matches[-1]
        # Accept comment only if there's no intervening non-whitespace code
        between = preceding[last.end():]
        if not re.search(r'\S', between):
            return last.group("text").strip()

    # Fallback: look for <!-- … --> comment
    matches = list(_HTML_COMMENT_RE.finditer(preceding))
    if matches:
        last = matches[-1]
        between = preceding[last.end():]
        if not re.search(r'\S', between):
            return last.group("text").strip()

    return ""


# ───────────────────────────────────────────────
# Main parser
# ───────────────────────────────────────────────

def _is_required(attrs: Dict[str, str]) -> bool:
    """Return True when the ``required`` attribute is present and not explicitly false.

    In JSX, a bare ``required`` attribute (no value) is equivalent to
    ``required={true}``.  We also accept the string ``"true"``.
    """
    if "required" not in attrs:
        return False
    val = attrs["required"].lower()
    # Bare attribute → empty string; treat as true
    return val not in {"false", "0"}


def _detect_element_type(tag: str, attrs: Dict[str, str]) -> ElementType:
    """Determine ElementType from tag name and type attribute."""
    tag_lower = tag.lower()
    if tag_lower in _HTML_ELEMENTS:
        if tag_lower == "input":
            t = attrs.get("type", "").lower()
            if t == "checkbox":
                return ElementType.CHECKBOX
            if t == "radio":
                return ElementType.RADIO
        return _HTML_ELEMENTS[tag_lower]
    if _PASCAL_RE.match(tag):
        return ElementType.CUSTOM
    return ElementType.UNKNOWN


def parse_jsx_file(filepath: str) -> List[UIElement]:
    """Parse a JSX/TSX file and return all detected UI elements.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the JSX/TSX source file.

    Returns
    -------
    list[UIElement]
        Ordered list of UI elements found in the file.
    """
    path = Path(filepath)
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    elements: List[UIElement] = []
    lines = source.splitlines(keepends=True)

    # Build a cumulative offset → line number map for fast lookup
    offsets: List[int] = []
    cumulative = 0
    for line in lines:
        offsets.append(cumulative)
        cumulative += len(line)

    def _line_number(pos: int) -> int:
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1  # 1-based

    for m in _TAG_RE.finditer(source):
        tag = m.group("tag")
        attrs_str = m.group("attrs")

        # Skip closing-tag lookalikes and obvious non-element tags
        if tag.lower() in {"script", "style", "link", "meta", "head", "html", "body", "div",
                           "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
                           "ul", "ol", "li", "table", "tr", "td", "th",
                           "form", "label", "a", "img", "svg", "path",
                           "section", "article", "nav", "main", "footer", "header",
                           "aside", "figure", "figcaption", "pre", "code"}:
            continue

        et = _detect_element_type(tag, {})
        if et == ElementType.UNKNOWN:
            continue

        attrs = _parse_attrs(attrs_str)
        et = _detect_element_type(tag, attrs)  # re-detect with attrs (checkbox/radio)

        elem = UIElement(
            element_id=attrs.get("id", ""),
            name=attrs.get("name", ""),
            type=attrs.get("type", ""),
            component_type=et,
            required=_is_required(attrs),
            placeholder=attrs.get("placeholder", ""),
            default_value=attrs.get("defaultValue", attrs.get("value", "")),
            event_handlers=_extract_event_handlers(attrs),
            comment=_preceding_comment(source, m.start()),
            line_number=_line_number(m.start()),
        )

        # maxLength / maxlength
        ml_raw = attrs.get("maxLength", attrs.get("maxlength", ""))
        if ml_raw.isdigit():
            elem.max_length = int(ml_raw)

        elements.append(elem)

    return elements
