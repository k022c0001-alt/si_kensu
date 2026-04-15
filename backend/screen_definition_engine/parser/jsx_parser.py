"""JSX UI element extractor for screen definition generation.

Parses a single JSX/TSX file and returns a list of UIElement objects
describing every form element found in the source.

Class-based API
---------------
    parser = JSXParser()
    elements = parser.parse_file('components/UserForm.jsx')

Functional API (retained for backwards compatibility)
------------------------------------------------------
    elements = parse_jsx_file('components/UserForm.jsx')
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


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

# Tags that are never UI form elements and should be skipped.
_EXCLUDED_TAGS: frozenset[str] = frozenset([
    "script", "style", "link", "meta", "head", "html", "body",
    "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "table", "tr", "td", "th",
    "form", "label", "a", "img", "svg", "path",
    "section", "article", "nav", "main", "footer", "header",
    "aside", "figure", "figcaption", "pre", "code",
])

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


# ───────────────────────────────────────────────
# Class-based API
# ───────────────────────────────────────────────

class JSXParser:
    """JSX/TSX UI element extractor with configurable rules.

    Parameters
    ----------
    config : dict, optional
        Override any of the default configuration keys:

        ``standard_elements``
            Mapping of lowercase HTML tag name → ElementType.
        ``custom_components``
            List of well-known PascalCase component names (informational).
            All PascalCase components not matching ``exclude_patterns`` are
            extracted as :attr:`ElementType.CUSTOM` regardless of this list.
        ``exclude_patterns``
            List of regex pattern strings.  Tags whose source text matches
            any pattern are skipped.
        ``comment_regex``
            (Informational) Regex string describing comment syntax.
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "standard_elements": {
            "input": ElementType.INPUT,
            "button": ElementType.BUTTON,
            "select": ElementType.SELECT,
            "textarea": ElementType.TEXTAREA,
        },
        "custom_components": [
            "CustomButton", "FormInput", "FormField", "TextInput", "SelectField",
        ],
        "exclude_patterns": [
            r"<div\b", r"<span\b", r"<Fragment", r"<>", r"<Icon\b",
        ],
        "comment_regex": r"//\s*(.+?)(?=\n|$)|/\*\s*([\s\S]*?)\*/",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        cfg: Dict[str, Any] = dict(self.DEFAULT_CONFIG)
        if config:
            cfg.update(config)
        self._config = cfg
        self._standard_elements: Dict[str, ElementType] = cfg["standard_elements"]
        self._exclude_patterns: List[re.Pattern] = [
            re.compile(p) for p in cfg.get("exclude_patterns", [])
        ]

        # Per-parse state – reset by parse_file()
        self._source: str = ""
        self._offsets: List[int] = []

    # ── Public API ────────────────────────────────

    def parse_file(self, file_path: str) -> List[UIElement]:
        """Parse a JSX/TSX file and return all detected UI elements.

        Parameters
        ----------
        file_path : str
            Absolute or relative path to the source file.

        Returns
        -------
        list[UIElement]
        """
        path = Path(file_path)
        try:
            self._source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(
                f"[JSXParser] Cannot read {file_path}: {exc}",
                file=sys.stderr,
            )
            return []
        self._build_line_map()
        return self._extract_elements()

    # ── Private helpers ───────────────────────────

    def _build_line_map(self) -> None:
        """Populate ``_offsets`` with the byte offset of each line start."""
        self._offsets = []
        cumulative = 0
        for line in self._source.splitlines(keepends=True):
            self._offsets.append(cumulative)
            cumulative += len(line)

    def _line_number(self, pos: int) -> int:
        """Return 1-based line number for byte offset *pos*."""
        offsets = self._offsets
        if not offsets:
            return 1
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    def _extract_elements(self) -> List[UIElement]:
        """Combine standard and custom element results sorted by line."""
        standard = self._extract_standard_elements()
        custom = self._extract_custom_components()
        combined = standard + custom
        combined.sort(key=lambda e: e.line_number)
        return combined

    def _extract_comments(self) -> Dict[int, str]:
        """Return a mapping of comment end-offset → comment text."""
        result: Dict[int, str] = {}
        for m in _COMMENT_RE.finditer(self._source):
            result[m.end()] = m.group("text").strip()
        for m in _HTML_COMMENT_RE.finditer(self._source):
            result[m.end()] = m.group("text").strip()
        return result

    def _extract_standard_elements(self) -> List[UIElement]:
        """Extract standard HTML form elements (input, button, select, textarea)."""
        elements: List[UIElement] = []
        for m in _TAG_RE.finditer(self._source):
            tag = m.group("tag")
            tag_lower = tag.lower()
            if tag_lower not in self._standard_elements:
                continue
            attrs = self._parse_attributes(m.group("attrs"))
            et = self._standard_elements[tag_lower]
            if tag_lower == "input":
                t = attrs.get("type", "").lower()
                if t == "checkbox":
                    et = ElementType.CHECKBOX
                elif t == "radio":
                    et = ElementType.RADIO
            elem = UIElement(
                element_id=attrs.get("id", ""),
                name=attrs.get("name", ""),
                type=attrs.get("type", ""),
                component_type=et,
                required=self._is_required(attrs),
                placeholder=attrs.get("placeholder", ""),
                default_value=attrs.get("defaultValue", attrs.get("value", "")),
                event_handlers=self._extract_event_handlers(attrs),
                comment=self._extract_preceding_comment(m.start()),
                line_number=self._line_number(m.start()),
            )
            ml_raw = attrs.get("maxLength", attrs.get("maxlength", ""))
            if ml_raw.isdigit():
                elem.max_length = int(ml_raw)
            elements.append(elem)
        return elements

    def _extract_custom_components(self) -> List[UIElement]:
        """Extract PascalCase custom components."""
        elements: List[UIElement] = []
        for m in _TAG_RE.finditer(self._source):
            tag = m.group("tag")
            if not _PASCAL_RE.match(tag):
                continue
            if self._should_exclude(m.start()):
                continue
            attrs = self._parse_attributes(m.group("attrs"))
            elem = UIElement(
                element_id=attrs.get("id", ""),
                name=attrs.get("name", attrs.get("label", "")),
                type=attrs.get("type", ""),
                component_type=ElementType.CUSTOM,
                required=self._is_required(attrs),
                placeholder=attrs.get("placeholder", ""),
                default_value=attrs.get("defaultValue", attrs.get("value", "")),
                event_handlers=self._extract_event_handlers(attrs),
                comment=self._extract_preceding_comment(m.start()),
                line_number=self._line_number(m.start()),
            )
            ml_raw = attrs.get("maxLength", attrs.get("maxlength", ""))
            if ml_raw.isdigit():
                elem.max_length = int(ml_raw)
            elements.append(elem)
        return elements

    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """Delegate to module-level attribute parser."""
        return _parse_attrs(attrs_str)

    def _extract_event_handlers(self, attrs: Dict[str, str]) -> Dict[str, str]:
        """Delegate to module-level event handler extractor."""
        return _extract_event_handlers(attrs)

    def _extract_preceding_comment(self, pos: int) -> str:
        """Delegate to module-level comment extractor."""
        return _preceding_comment(self._source, pos)

    def _should_exclude(self, pos: int) -> bool:
        """Return True if the source text at *pos* matches any exclude pattern."""
        text = self._source[pos : pos + 100]
        return any(p.match(text) for p in self._exclude_patterns)

    @staticmethod
    def _is_required(attrs: Dict[str, str]) -> bool:
        """Delegate to module-level required-attribute checker."""
        return _is_required(attrs)


# ───────────────────────────────────────────────
# Functional API (backwards compatible)
# ───────────────────────────────────────────────

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

        # Skip excluded structural/non-form tags
        if tag.lower() in _EXCLUDED_TAGS:
            continue

        # Parse attributes first so element type detection can use them
        attrs = _parse_attrs(attrs_str)
        et = _detect_element_type(tag, attrs)
        if et == ElementType.UNKNOWN:
            continue

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
