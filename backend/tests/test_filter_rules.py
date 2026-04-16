"""
test_filter_rules.py
FilterRule / FilterRuleSet のユニットテスト

テスト対象:
  - FilterRule クラス
  - FilterRuleSet クラス
  - DEFAULT_RULES / STRICT_RULES
  - apply_all() / apply_any() 関数
  - AND / OR 条件
  - カスタム規則
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from screen_definition_engine.parser.jsx_parser import ElementType, UIElement
from screen_definition_engine.filter.filter_rules import (
    DEFAULT_RULES,
    STRICT_RULES,
    FilterRule,
    FilterRuleSet,
    apply_all,
    apply_any,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_elem(
    element_id: str = "field-id",
    name: str = "fieldName",
    required: bool = False,
    component_type: ElementType = ElementType.INPUT,
) -> UIElement:
    return UIElement(
        element_id=element_id,
        name=name,
        required=required,
        component_type=component_type,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FilterRule テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestFilterRule:
    def test_rule_passes_when_condition_true(self):
        rule = FilterRule("always_pass", lambda e: True)
        elem = _make_elem()
        assert rule.apply(elem) is True

    def test_rule_fails_when_condition_false(self):
        rule = FilterRule("always_fail", lambda e: False)
        elem = _make_elem()
        assert rule.apply(elem) is False

    def test_rule_name_stored(self):
        rule = FilterRule("my_rule", lambda e: True)
        assert rule.name == "my_rule"

    def test_passes_is_alias_for_apply(self):
        rule = FilterRule("check_required", lambda e: e.required)
        elem_req = _make_elem(required=True)
        elem_opt = _make_elem(required=False)
        assert rule.passes(elem_req) is True
        assert rule.passes(elem_opt) is False

    def test_rule_with_element_attribute_check(self):
        rule = FilterRule("has_id", lambda e: bool(e.element_id))
        assert rule.apply(_make_elem(element_id="some-id")) is True
        assert rule.apply(_make_elem(element_id="")) is False


# ─────────────────────────────────────────────────────────────────────────────
# FilterRuleSet テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestFilterRuleSet:
    def test_normal_mode_default(self):
        rs = FilterRuleSet()
        # has_identifier + not_placeholder のデフォルトルール
        valid = _make_elem(element_id="valid-id")
        assert len(rs.apply_all([valid])) == 1

    def test_normal_mode_excludes_no_id(self):
        rs = FilterRuleSet(mode="normal")
        no_id = _make_elem(element_id="", name="")
        assert len(rs.apply_all([no_id])) == 0

    def test_strict_mode_excludes_no_name(self):
        rs = FilterRuleSet(mode="strict")
        no_name = _make_elem(element_id="some-id", name="")
        assert len(rs.apply_all([no_name])) == 0

    def test_strict_mode_passes_full_element(self):
        rs = FilterRuleSet(mode="strict")
        full = _make_elem(element_id="full-id", name="fullName")
        assert len(rs.apply_all([full])) == 1

    def test_add_rule_custom(self):
        rs = FilterRuleSet(mode="normal")
        rs.add_rule(FilterRule("required_only", lambda e: e.required))
        req = _make_elem(element_id="req-id", name="req", required=True)
        opt = _make_elem(element_id="opt-id", name="opt", required=False)
        result = rs.apply_all([req, opt])
        assert len(result) == 1
        assert result[0].element_id == "req-id"

    def test_apply_all_and_logic(self):
        """AND 条件: 全ルールを通過しないと除外される"""
        rs = FilterRuleSet(mode="normal")
        rs.add_rule(FilterRule("button_only", lambda e: e.component_type == ElementType.BUTTON))
        input_elem = _make_elem(element_id="inp-id", name="inp", component_type=ElementType.INPUT)
        button_elem = _make_elem(element_id="btn-id", name="btn", component_type=ElementType.BUTTON)
        result = rs.apply_all([input_elem, button_elem])
        assert len(result) == 1
        assert result[0].element_id == "btn-id"

    def test_apply_any_or_logic(self):
        """OR 条件: 1つでもルールを通過すれば残る"""
        rs = FilterRuleSet(mode="normal")
        rs.add_rule(FilterRule("button_only", lambda e: e.component_type == ElementType.BUTTON))
        input_elem = _make_elem(element_id="inp-id", name="inp", component_type=ElementType.INPUT)
        button_elem = _make_elem(element_id="btn-id", name="btn", component_type=ElementType.BUTTON)
        # apply_any は既存のルール OR 新しいルール
        result = rs.apply_any([input_elem, button_elem])
        assert len(result) >= 1

    def test_apply_all_empty_list(self):
        rs = FilterRuleSet()
        assert rs.apply_all([]) == []

    def test_apply_any_empty_list(self):
        rs = FilterRuleSet()
        assert rs.apply_any([]) == []


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT_RULES / STRICT_RULES テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltinRules:
    def test_default_rules_not_empty(self):
        assert len(DEFAULT_RULES) >= 2

    def test_strict_rules_more_than_default(self):
        assert len(STRICT_RULES) >= len(DEFAULT_RULES)

    def test_default_rules_are_filter_rule_instances(self):
        for rule in DEFAULT_RULES:
            assert isinstance(rule, FilterRule)

    def test_strict_rules_includes_has_name(self):
        names = [r.name for r in STRICT_RULES]
        assert "has_name" in names


# ─────────────────────────────────────────────────────────────────────────────
# apply_all / apply_any 関数テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestApplyFunctions:
    def test_apply_all_passes_valid_element(self):
        elems = [_make_elem(element_id="valid-id", name="valid")]
        result = apply_all(elems)
        assert len(result) == 1

    def test_apply_all_excludes_no_identifier(self):
        elems = [_make_elem(element_id="", name="")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_all_excludes_debug_pattern(self):
        elems = [_make_elem(element_id="debug-input", name="debug")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_all_excludes_temp_pattern(self):
        elems = [_make_elem(element_id="temp-field", name="temp")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_all_excludes_unused_pattern(self):
        elems = [_make_elem(element_id="unused-input", name="unused")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_all_with_custom_rules(self):
        only_required = FilterRule("required_only", lambda e: e.required)
        elems = [
            _make_elem(element_id="req", name="req", required=True),
            _make_elem(element_id="opt", name="opt", required=False),
        ]
        result = apply_all(elems, rules=[only_required])
        assert len(result) == 1
        assert result[0].element_id == "req"

    def test_apply_any_single_rule(self):
        rule = FilterRule("has_id", lambda e: bool(e.element_id))
        elems = [
            _make_elem(element_id="has-id"),
            _make_elem(element_id=""),
        ]
        result = apply_any(elems, [rule])
        assert len(result) == 1
        assert result[0].element_id == "has-id"

    def test_apply_any_multiple_rules_or_logic(self):
        rule_id = FilterRule("has_id", lambda e: bool(e.element_id))
        rule_name = FilterRule("has_name", lambda e: bool(e.name))
        elems = [
            _make_elem(element_id="has-id", name=""),
            _make_elem(element_id="", name="has-name"),
            _make_elem(element_id="", name=""),
        ]
        result = apply_any(elems, [rule_id, rule_name])
        assert len(result) == 2

    def test_apply_all_empty_input(self):
        assert apply_all([]) == []

    def test_apply_any_empty_input(self):
        assert apply_any([], [FilterRule("any", lambda e: True)]) == []
