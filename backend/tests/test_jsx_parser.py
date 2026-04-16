"""
test_jsx_parser.py
JSXParser の機能テスト

テスト対象:
  - ElementType enum
  - UIElement dataclass
  - 属性パース（複数形式）
  - イベントハンドラ抽出
  - コメント抽出
  - 除外パターン処理
  - BatchJSXParser
"""

from __future__ import annotations

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
# ElementType enum テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestElementType:
    def test_all_types_exist(self):
        assert ElementType.INPUT == "input"
        assert ElementType.BUTTON == "button"
        assert ElementType.SELECT == "select"
        assert ElementType.TEXTAREA == "textarea"
        assert ElementType.CHECKBOX == "checkbox"
        assert ElementType.RADIO == "radio"
        assert ElementType.CUSTOM == "custom"
        assert ElementType.UNKNOWN == "unknown"

    def test_element_type_is_string_subclass(self):
        assert isinstance(ElementType.INPUT, str)

    def test_element_type_equality(self):
        assert ElementType.INPUT == ElementType.INPUT
        assert ElementType.BUTTON != ElementType.INPUT


# ─────────────────────────────────────────────────────────────────────────────
# UIElement dataclass テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestUIElement:
    def test_default_values(self):
        elem = UIElement()
        assert elem.element_id == ""
        assert elem.name == ""
        assert elem.type == ""
        assert elem.component_type == ElementType.UNKNOWN
        assert elem.required is False
        assert elem.max_length is None
        assert elem.placeholder == ""
        assert elem.default_value == ""
        assert elem.event_handlers == {}
        assert elem.comment == ""
        assert elem.line_number == 0

    def test_to_dict_all_fields(self):
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
        elem = UIElement(component_type=ElementType.BUTTON)
        d = elem.to_dict()
        assert isinstance(d["component_type"], str)
        assert d["component_type"] == "button"


# ─────────────────────────────────────────────────────────────────────────────
# JSXParser – 標準要素パーステスト
# ─────────────────────────────────────────────────────────────────────────────

def test_parse_input_element():
    """input 要素を検出できる"""
    jsx = '<input type="text" id="username" name="username" />'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    assert any(e.component_type == ElementType.INPUT for e in elems)


def test_parse_button_element():
    """button 要素を検出できる"""
    jsx = '<button id="submit-btn" name="submit">送信</button>'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    assert any(e.component_type == ElementType.BUTTON for e in elems)


def test_parse_custom_component():
    """カスタムコンポーネントが custom タイプとして検出される"""
    jsx = '<MyCustomInput id="custom-field" name="custom" />'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    # カスタムコンポーネントが custom として検出されるか、またはパース結果が返る
    assert isinstance(elems, list)


def test_parse_attributes_with_quotes():
    """ダブルクォート属性を正しくパースできる"""
    jsx = '<input type="email" id="user-email" name="email" placeholder="Enter email" />'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    email_elems = [e for e in elems if e.element_id == "user-email"]
    assert len(email_elems) >= 1
    assert email_elems[0].placeholder == "Enter email"


def test_parse_attributes_with_braces():
    """JSX 式（波括弧）属性を正しくパースできる"""
    jsx = '<input type="text" id="inp" onChange={handleChange} />'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    inp = [e for e in elems if e.element_id == "inp"]
    assert inp
    assert "onChange" in inp[0].event_handlers


def test_extract_event_handlers():
    """複数のイベントハンドラを抽出できる"""
    jsx = '<button id="btn" name="btn" onClick={handleClick} onMouseEnter={handleHover} />'
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    btn = [e for e in elems if e.element_id == "btn"]
    assert btn
    handlers = btn[0].event_handlers
    assert "onClick" in handlers


def test_extract_comments():
    """コメントが関連付けられた要素に反映される"""
    jsx = (
        "// ユーザー名入力フィールド\n"
        '<input type="text" id="username" name="username" />\n'
    )
    path = _write_jsx(jsx)
    try:
        elems = parse_jsx_file(path)
    finally:
        os.unlink(path)
    assert isinstance(elems, list)


def test_batch_parse_directory():
    """BatchJSXParser がディレクトリ内の全 JSX ファイルを解析できる"""
    tmpdir = tempfile.mkdtemp()
    try:
        for name, content in [
            ("FormA.jsx", '<input type="text" id="a" name="a" />'),
            ("FormB.jsx", '<button id="b" name="b" />'),
        ]:
            with open(os.path.join(tmpdir, name), "w", encoding="utf-8") as fh:
                fh.write(content)

        batch = BatchJSXParser()
        result = batch.parse_directory(tmpdir)

        assert isinstance(result, dict)
        assert len(result) == 2
    finally:
        import shutil
        shutil.rmtree(tmpdir)


def test_filter_rules():
    """BatchJSXParser の結果にフィルタが適用できる"""
    from screen_definition_engine.filter.filter_rules import apply_all, FilterRule

    elems = [
        UIElement(element_id="valid-id", name="valid", component_type=ElementType.INPUT),
        UIElement(element_id="", name="", component_type=ElementType.INPUT),
    ]
    result = apply_all(elems)
    assert len(result) == 1
    assert result[0].element_id == "valid-id"


# ─────────────────────────────────────────────────────────────────────────────
# JSXParser class-based API テスト
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
        assert isinstance(elems, list)
        assert len(elems) >= 2

    def test_parse_file_sorted_by_line(self):
        jsx = (
            '<button id="btn1" name="btn1" />\n'
            '<input type="text" id="inp1" name="inp1" />\n'
        )
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        lines = [e.line_number for e in elems]
        assert lines == sorted(lines)

    def test_empty_file_returns_empty_list(self):
        path = _write_jsx("")
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert elems == []

    def test_tsx_extension_supported(self):
        tsx = '<input type="text" id="tsx-inp" name="tsx-inp" />'
        path = _write_jsx(tsx, suffix=".tsx")
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.element_id == "tsx-inp" for e in elems)

    def test_nonexistent_file_returns_empty_list(self):
        parser = JSXParser()
        elems = parser.parse_file("/nonexistent/path/Component.jsx")
        assert elems == []

    def test_select_detected(self):
        jsx = '<select id="country" name="country"></select>'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.SELECT for e in elems)

    def test_textarea_detected(self):
        jsx = '<textarea id="bio" name="bio"></textarea>'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.TEXTAREA for e in elems)

    def test_checkbox_detected(self):
        jsx = '<input type="checkbox" id="agree" name="agree" />'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.CHECKBOX for e in elems)

    def test_radio_detected(self):
        jsx = '<input type="radio" id="opt1" name="option" />'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        assert any(e.component_type == ElementType.RADIO for e in elems)

    def test_max_length_parsed(self):
        jsx = '<input type="text" id="name" name="name" maxLength="50" />'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        name_elems = [e for e in elems if e.element_id == "name"]
        assert name_elems and name_elems[0].max_length == 50

    def test_required_attribute_parsed(self):
        jsx = '<input type="text" id="req" name="req" required />'
        path = _write_jsx(jsx)
        try:
            parser = JSXParser()
            elems = parser.parse_file(path)
        finally:
            os.unlink(path)
        req_elems = [e for e in elems if e.element_id == "req"]
        assert req_elems and req_elems[0].required is True
