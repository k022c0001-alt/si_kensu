"""Rule-based filter for UIElement lists.

Each FilterRule wraps a callable ``condition(UIElement) -> bool``.
When the condition returns *False*, the element is excluded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
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

    def apply(self, element: UIElement) -> bool:
        """Return True if the element passes this rule."""
        return self.condition(element)

    def passes(self, element: UIElement) -> bool:
        """Alias for apply() – retained for backwards compatibility."""
        return self.apply(element)


# ───────────────────────────────────────────────
# Built-in rules
# ───────────────────────────────────────────────

_IGNORE_PATTERNS = re.compile(
    r"(?:^|_|-)(temp|debug|unused|placeholder|dummy|mock|test)(?:$|_|-)",
    re.IGNORECASE,
)


def _has_name(elem: UIElement) -> bool:
    """Element must have a non-empty name."""
    return bool(elem.name.strip())


def _has_identifier(elem: UIElement) -> bool:
    """Element must have a non-empty element_id."""
    return bool(elem.element_id)


def _not_placeholder(elem: UIElement) -> bool:
    """Exclude elements whose id contains temp/debug/unused patterns."""
    eid = elem.element_id.lower()
    return not any(x in eid for x in ["temp", "debug", "unused"])


# Default rule set applied by FilterRuleSet (normal mode)
DEFAULT_RULES: List[FilterRule] = [
    FilterRule("has_identifier", _has_identifier),
    FilterRule("not_placeholder", _not_placeholder),
]

# Strict mode adds the has_name rule on top of the defaults
STRICT_RULES: List[FilterRule] = [
    FilterRule("has_name", _has_name),
    FilterRule("has_identifier", _has_identifier),
    FilterRule("not_placeholder", _not_placeholder),
]


# ───────────────────────────────────────────────
# FilterRuleSet
# ───────────────────────────────────────────────

class FilterRuleSet:
    """Manage and apply multiple :class:`FilterRule` instances.

    Parameters
    ----------
    mode : str
        ``"strict"`` – applies has_name + has_identifier + not_placeholder.
        Any other value uses the normal default rules.
    """

    def __init__(self, mode: str = "normal") -> None:
        self._rules: List[FilterRule] = []
        self._mode = mode
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Populate the rule list with defaults based on the current mode."""
        if self._mode == "strict":
            self._rules = list(STRICT_RULES)
        else:
            self._rules = list(DEFAULT_RULES)

    def add_rule(self, rule: FilterRule) -> None:
        """Append a custom rule to the set."""
        self._rules.append(rule)

    def apply_all(self, elements: List[UIElement]) -> List[UIElement]:
        """Keep elements that satisfy **all** rules (AND logic)."""
        result = []
        for elem in elements:
            if all(r.apply(elem) for r in self._rules):
                result.append(elem)
        return result

    def apply_any(self, elements: List[UIElement]) -> List[UIElement]:
        """Keep elements that satisfy **at least one** rule (OR logic)."""
        result = []
        for elem in elements:
            if any(r.apply(elem) for r in self._rules):
                result.append(elem)
        return result


# ───────────────────────────────────────────────
# Functional API (backwards compatible)
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
        if all(r.apply(elem) for r in rules):
            result.append(elem)
    return result


def apply_any(
    elements: List[UIElement],
    rules: List[FilterRule],
) -> List[UIElement]:
    """Keep elements that satisfy **at least one** rule (OR logic)."""
    result = []
    for elem in elements:
        if any(r.apply(elem) for r in rules):
            result.append(elem)
    return result
