"""
test_screen_definition.py
screen_definition_engine のユニットテスト

テスト対象:
  - JSXParser  (jsx_parser.py)
  - BatchJSXParser (jsx_parser_batch.py)
  - filter_rules  (filter_rules.py)
  - screen_handler (ipc/screen_handler.py)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from screen_definition_engine.parser.jsx_parser import (
    ElementType,
    JSXParser,
    UIElement,
    parse_jsx_file,
)
from screen_definition_engine.parser.jsx_parser_batch import (
    BatchJSXParser,
    parse_directory,
)
from screen_definition_engine.filter.filter_rules import (
    DEFAULT_RULES,
    FilterRule,
    apply_all,
    apply_any,
)
from screen_definition_engine.ipc.screen_handler import handle_request


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _write_jsx(content: str, suffix: str = ".jsx") -> str:
    """Write content to a temporary JSX file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# UIElement.to_dict()
# ─────────────────────────────────────────────────────────────────────────────

class TestUIElement:
    def test_to_dict_contains_all_fields(self):
        elem = UIElement(
            element_id="user-email",
            name="email",
            type="email",
            component_type=ElementType.INPUT,
            required=True,
            max_length=120,
            placeholder="Enter email",
            default_value="",
            event_handlers={"onChange": "handleChange"},
            comment="User email field",
            line_number=5,
        )
        d = elem.to_dict()
        assert d["element_id"] == "user-email"
        assert d["name"] == "email"
        assert d["type"] == "email"
        assert d["component_type"] == "input"
        assert d["required"] is True
        assert d["max_length"] == 120
        assert d["placeholder"] == "Enter email"
        assert d["event_handlers"] == {"onChange": "handleChange"}
        assert d["comment"] == "User email field"
        assert d["line_number"] == 5

    def test_to_dict_component_type_is_string(self):
        """component_type は ElementType enum でなく文字列で返る"""
        elem = UIElement(component_type=ElementType.BUTTON)
        assert isinstance(elem.to_dict()["component_type"], str)


# ─────────────────────────────────────────────────────────────────────────────
# JSXParser – 標準 HTML フォーム要素
# ─────────────────────────────────────────────────────────────────────────────

class TestJSXParserStandardElements:
    def test_input_text_detected(self):
        jsx = '<input type="text" id="username" name="username" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.INPUT for e in elems)

    def test_input_checkbox_detected(self):
        jsx = '<input type="checkbox" id="agree" name="agree" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.CHECKBOX for e in elems)

    def test_input_radio_detected(self):
        jsx = '<input type="radio" id="opt1" name="option" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.RADIO for e in elems)

    def test_button_detected(self):
        jsx = '<button id="submit-btn" name="submit" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.BUTTON for e in elems)

    def test_select_detected(self):
        jsx = '<select id="country" name="country"></select>'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.SELECT for e in elems)

    def test_textarea_detected(self):
        jsx = '<textarea id="bio" name="bio"></textarea>'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.TEXTAREA for e in elems)

    def test_required_attribute_parsed(self):
        jsx = '<input type="text" id="req" name="req" required />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        req_elems = [e for e in elems if e.element_id == "req"]
        assert req_elems and req_elems[0].required is True

    def test_max_length_parsed(self):
        jsx = '<input type="text" id="name" name="name" maxLength="50" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        name_elems = [e for e in elems if e.element_id == "name"]
        assert name_elems and name_elems[0].max_length == 50

    def test_placeholder_parsed(self):
        jsx = '<input type="text" id="ph" placeholder="Enter value" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        ph_elems = [e for e in elems if e.element_id == "ph"]
        assert ph_elems and ph_elems[0].placeholder == "Enter value"

    def test_event_handler_extracted(self):
        jsx = '<input type="text" id="inp" onChange={handleChange} />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        inp = [e for e in elems if e.element_id == "inp"]
        assert inp and "onChange" in inp[0].event_handlers

    def test_line_number_positive(self):
        jsx = '\n\n<input type="text" id="inp2" name="inp2" />'
        path = _write_jsx(jsx)
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert all(e.line_number > 0 for e in elems)

    def test_empty_file_returns_empty_list(self):
        path = _write_jsx("")
        try:
            elems = parse_jsx_file(path)
        finally:
            os.unlink(path)
        assert elems == []

    def test_nonexistent_file_returns_empty_list(self):
        elems = parse_jsx_file("/nonexistent/path/Component.jsx")
        assert elems == []


# ─────────────────────────────────────────────────────────────────────────────
# JSXParser (class-based API)
# ─────────────────────────────────────────────────────────────────────────────

class TestJSXParserClassAPI:
    def test_parse_file_returns_list(self):
        jsx = '<input type="text" id="a" name="a" /><button id="b" name="b" />'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert len(elems) >= 2

    def test_parse_file_sorted_by_line(self):
        jsx = (
            "<button id='btn1' name='btn1' />\n"
            "<input type='text' id='inp1' name='inp1' />\n"
        )
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        lines = [e.line_number for e in elems]
        assert lines == sorted(lines)

    def test_tsx_extension_supported(self):
        tsx = '<input type="text" id="tsx-inp" name="tsx-inp" />'
        path = _write_jsx(tsx, suffix=".tsx")
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.element_id == "tsx-inp" for e in elems)


# ─────────────────────────────────────────────────────────────────────────────
# BatchJSXParser
# ─────────────────────────────────────────────────────────────────────────────

class TestBatchJSXParser:
    def _make_component_dir(self) -> str:
        """Create a temp directory with two JSX files."""
        tmpdir = tempfile.mkdtemp()
        for name, content in [
            ("FormA.jsx", '<input type="text" id="a" name="a" />'),
            ("FormB.jsx", '<button id="b" name="b" />'),
        ]:
            with open(os.path.join(tmpdir, name), "w", encoding="utf-8") as fh:
                fh.write(content)
        return tmpdir

    def test_parse_directory_returns_dict(self):
        tmpdir = self._make_component_dir()
        try:
            batch = BatchJSXParser()
            result = batch.parse_directory(tmpdir)
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert isinstance(result, dict)
        assert len(result) == 2

    def test_all_files_present_in_result(self):
        tmpdir = self._make_component_dir()
        try:
            batch = BatchJSXParser()
            result = batch.parse_directory(tmpdir)
        finally:
            import shutil; shutil.rmtree(tmpdir)
        keys = list(result.keys())
        assert any("FormA" in k for k in keys)
        assert any("FormB" in k for k in keys)

    def test_functional_parse_directory(self):
        tmpdir = self._make_component_dir()
        try:
            result = parse_directory(tmpdir)
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert result["root"] == tmpdir
        assert len(result["files"]) == 2
        assert result["total_elements"] >= 2


# ─────────────────────────────────────────────────────────────────────────────
# FilterRule / apply_all / apply_any
# ─────────────────────────────────────────────────────────────────────────────

class TestFilterRules:
    def _make_elem(self, element_id="", name="") -> UIElement:
        return UIElement(element_id=element_id, name=name,
                         component_type=ElementType.INPUT)

    def test_apply_all_passes_when_all_rules_satisfied(self):
        elems = [self._make_elem(element_id="user-email", name="email")]
        result = apply_all(elems)
        assert len(result) == 1

    def test_apply_all_excludes_when_no_identifier(self):
        elems = [self._make_elem(element_id="", name="")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_all_excludes_ignored_pattern(self):
        elems = [self._make_elem(element_id="debug-input", name="debug")]
        result = apply_all(elems)
        assert len(result) == 0

    def test_apply_any_passes_when_any_rule_satisfied(self):
        rule = FilterRule("has_id", lambda e: bool(e.element_id))
        elems = [
            self._make_elem(element_id="has-id", name=""),
            self._make_elem(element_id="", name="has-name"),
        ]
        result = apply_any(elems, [rule])
        assert len(result) == 1

    def test_custom_rule_filters_correctly(self):
        """カスタムルールを追加して正しくフィルタリングできる"""
        only_required = FilterRule("required_only", lambda e: e.required)
        elems = [
            UIElement(element_id="req", name="req",
                      component_type=ElementType.INPUT, required=True),
            UIElement(element_id="opt", name="opt",
                      component_type=ElementType.INPUT, required=False),
        ]
        result = apply_all(elems, rules=[only_required])
        assert len(result) == 1
        assert result[0].element_id == "req"

    def test_default_rules_exported(self):
        assert len(DEFAULT_RULES) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# IPC screen_handler – handle_request()
# ─────────────────────────────────────────────────────────────────────────────

class TestScreenHandler:
    def _make_dir_with_jsx(self) -> str:
        tmpdir = tempfile.mkdtemp()
        content = '<input type="text" id="field1" name="field1" />'
        with open(os.path.join(tmpdir, "Form.jsx"), "w", encoding="utf-8") as fh:
            fh.write(content)
        return tmpdir

    def test_parse_directory_success(self):
        tmpdir = self._make_dir_with_jsx()
        try:
            response = handle_request({"action": "parse_directory", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert "data" in response
        assert response["data"]["total_elements"] >= 1

    def test_parse_file_success(self):
        content = '<input type="text" id="fld" name="fld" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) >= 1

    def test_parse_file_missing_key_returns_error(self):
        response = handle_request({"action": "parse_file"})
        assert "error" in response

    def test_export_json_same_as_parse_directory(self):
        tmpdir = self._make_dir_with_jsx()
        try:
            r_parse = handle_request({"action": "parse_directory", "root": tmpdir})
            r_export = handle_request({"action": "export_json", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert r_parse["data"]["total_elements"] == r_export["data"]["total_elements"]

    def test_unknown_action_returns_error(self):
        response = handle_request({"action": "nonexistent_action"})
        assert "error" in response

    def test_filter_applied_by_default(self):
        """filter=True（デフォルト）の場合、名前・IDなしの要素は除外される"""
        content = '<input type="text" />'   # id も name もなし → フィルタで除外
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path, "filter": True})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) == 0

    def test_filter_false_returns_all(self):
        """filter=False の場合、名前・IDなしの要素も返る"""
        content = '<input type="text" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path, "filter": False})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) >= 1

    def test_nonexistent_directory_returns_empty(self):
        response = handle_request({
            "action": "parse_directory",
            "root": "/tmp/nonexistent_dir_12345",
        })
        assert "data" in response
        assert response["data"]["total_elements"] == 0
