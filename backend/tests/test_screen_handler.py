"""
test_screen_handler.py
screen_handler.py のエントリポイントテスト

テスト対象:
  - handle_request() – 各アクション
  - JSON パース
  - エラーハンドリング
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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


def _make_dir_with_jsx() -> str:
    """Create a temp directory with a JSX file containing a form input."""
    tmpdir = tempfile.mkdtemp()
    content = '<input type="text" id="field1" name="field1" />'
    with open(os.path.join(tmpdir, "Form.jsx"), "w", encoding="utf-8") as fh:
        fh.write(content)
    return tmpdir


# ─────────────────────────────────────────────────────────────────────────────
# parse_directory アクションテスト
# ─────────────────────────────────────────────────────────────────────────────

class TestParseDirectory:
    def test_success_returns_data(self):
        tmpdir = _make_dir_with_jsx()
        try:
            response = handle_request({"action": "parse_directory", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert "data" in response
        assert response["data"]["total_elements"] >= 1

    def test_response_structure(self):
        tmpdir = _make_dir_with_jsx()
        try:
            response = handle_request({"action": "parse_directory", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        data = response["data"]
        assert "files" in data
        assert "total_elements" in data
        assert isinstance(data["files"], list)
        assert isinstance(data["total_elements"], int)

    def test_nonexistent_directory_returns_empty(self):
        response = handle_request({
            "action": "parse_directory",
            "root": "/tmp/nonexistent_dir_si_kensu_12345",
        })
        assert "data" in response
        assert response["data"]["total_elements"] == 0

    def test_default_action_is_parse_directory(self):
        """action が省略された場合は parse_directory として動作する"""
        tmpdir = _make_dir_with_jsx()
        try:
            response = handle_request({"root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert "data" in response


# ─────────────────────────────────────────────────────────────────────────────
# parse_file アクションテスト
# ─────────────────────────────────────────────────────────────────────────────

class TestParseFile:
    def test_success_returns_data(self):
        content = '<input type="text" id="fld" name="fld" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) >= 1

    def test_response_structure(self):
        content = '<input type="text" id="fld2" name="fld2" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path})
        finally:
            os.unlink(path)
        data = response["data"]
        assert "file" in data
        assert "elements" in data
        assert isinstance(data["elements"], list)

    def test_missing_file_key_returns_error(self):
        response = handle_request({"action": "parse_file"})
        assert "error" in response

    def test_element_structure(self):
        content = '<input type="text" id="el1" name="el1" placeholder="Enter value" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path})
        finally:
            os.unlink(path)
        elements = response["data"]["elements"]
        assert len(elements) >= 1
        elem = elements[0]
        assert "element_id" in elem
        assert "component_type" in elem
        assert "line_number" in elem


# ─────────────────────────────────────────────────────────────────────────────
# export_json アクションテスト
# ─────────────────────────────────────────────────────────────────────────────

class TestExportJson:
    def test_same_result_as_parse_directory(self):
        tmpdir = _make_dir_with_jsx()
        try:
            r_parse = handle_request({"action": "parse_directory", "root": tmpdir})
            r_export = handle_request({"action": "export_json", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert r_parse["data"]["total_elements"] == r_export["data"]["total_elements"]

    def test_success(self):
        tmpdir = _make_dir_with_jsx()
        try:
            response = handle_request({"action": "export_json", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        assert "data" in response


# ─────────────────────────────────────────────────────────────────────────────
# フィルタ機能テスト
# ─────────────────────────────────────────────────────────────────────────────

class TestFilterBehavior:
    def test_filter_applied_by_default(self):
        """filter=True（デフォルト）の場合、名前・IDなし要素は除外される"""
        content = '<input type="text" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path, "filter": True})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) == 0

    def test_filter_false_returns_all(self):
        """filter=False の場合、名前・IDなし要素も返る"""
        content = '<input type="text" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path, "filter": False})
        finally:
            os.unlink(path)
        assert "data" in response
        assert len(response["data"]["elements"]) >= 1

    def test_multiple_elements_filtered(self):
        """複数要素のうちフィルタ対象のみ除外される"""
        content = (
            '<input type="text" id="valid" name="valid" />\n'
            '<input type="text" />\n'
        )
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path, "filter": True})
        finally:
            os.unlink(path)
        elements = response["data"]["elements"]
        ids = [e["element_id"] for e in elements]
        assert "valid" in ids


# ─────────────────────────────────────────────────────────────────────────────
# エラーハンドリングテスト
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandling:
    def test_unknown_action_returns_error(self):
        response = handle_request({"action": "nonexistent_action"})
        assert "error" in response

    def test_error_message_is_string(self):
        response = handle_request({"action": "nonexistent_action"})
        assert isinstance(response["error"], str)

    def test_parse_file_empty_path_returns_error(self):
        response = handle_request({"action": "parse_file", "file": ""})
        assert "error" in response

    def test_response_is_dict(self):
        response = handle_request({"action": "unknown_xyz"})
        assert isinstance(response, dict)


# ─────────────────────────────────────────────────────────────────────────────
# JSON 出力テスト（シリアライズ可能性）
# ─────────────────────────────────────────────────────────────────────────────

class TestJsonOutput:
    def test_parse_directory_response_is_json_serializable(self):
        tmpdir = _make_dir_with_jsx()
        try:
            response = handle_request({"action": "parse_directory", "root": tmpdir})
        finally:
            import shutil; shutil.rmtree(tmpdir)
        # JSON シリアライズ可能かチェック
        serialized = json.dumps(response)
        assert isinstance(serialized, str)

    def test_parse_file_response_is_json_serializable(self):
        content = '<input type="text" id="test-id" name="test-name" />'
        path = _write_jsx(content)
        try:
            response = handle_request({"action": "parse_file", "file": path})
        finally:
            os.unlink(path)
        serialized = json.dumps(response)
        assert isinstance(serialized, str)

    def test_error_response_is_json_serializable(self):
        response = handle_request({"action": "bad_action"})
        serialized = json.dumps(response)
        assert isinstance(serialized, str)
