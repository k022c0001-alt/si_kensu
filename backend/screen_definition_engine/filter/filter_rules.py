"""Rule-based filter for UIElement lists.

Each FilterRule wraps a callable ``condition(UIElement) -> bool``.
When the condition returns *False*, the element is excluded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List

from ..parser.jsx_parser import ElementType, UIElement


# ───────────────────────────────────────────────
# FilterRule
# ───────────────────────────────────────────────

@dataclass
class FilterRule:
    """A single named filter rule."""

    name: str
    condition: Callable[[UIElement], bool]

    def passes(self, element: UIElement) -> bool:
        return self.condition(element)


# ───────────────────────────────────────────────
# Built-in rules
# ───────────────────────────────────────────────

_IGNORE_PATTERNS = re.compile(
    r"(?:^|_|-)(temp|debug|unused|placeholder|dummy|mock|test)(?:$|_|-)",
    re.IGNORECASE,
)


def _has_identifier(elem: UIElement) -> bool:
    """Element must have a non-empty id or name."""
    return bool(elem.element_id or elem.name)


def _not_ignored_pattern(elem: UIElement) -> bool:
    """Exclude elements whose name/id matches common ignore patterns."""
    combined = elem.element_id + " " + elem.name
    return not bool(_IGNORE_PATTERNS.search(combined))


# Default rule set applied by apply_all()
DEFAULT_RULES: List[FilterRule] = [
    FilterRule("has_identifier", _has_identifier),
    FilterRule("not_ignored_pattern", _not_ignored_pattern),
]


# ───────────────────────────────────────────────
# Apply functions
# ───────────────────────────────────────────────

def apply_all(
    elements: List[UIElement],
    rules: List[FilterRule] | None = None,
) -> List[UIElement]:
    """Keep elements that satisfy **all** rules (AND logic).

    Parameters
    ----------
    elements : list[UIElement]
        Input elements to filter.
    rules : list[FilterRule] | None
        Rules to apply.  Defaults to ``DEFAULT_RULES``.

    Returns
    -------
    list[UIElement]
        Filtered elements.
    """
    if rules is None:
        rules = DEFAULT_RULES
    result = []
    for elem in elements:
        if all(r.passes(elem) for r in rules):
            result.append(elem)
    return result


def apply_any(
    elements: List[UIElement],
    rules: List[FilterRule],
) -> List[UIElement]:
    """Keep elements that satisfy **at least one** rule (OR logic)."""
    result = []
    for elem in elements:
        if any(r.passes(elem) for r in rules):
            result.append(elem)
    return result
