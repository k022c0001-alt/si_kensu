"""
test_layer_classifier.py
レイヤー分類 (layer/classifier.py) のユニットテスト
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.layer.classifier import classify_layer


class TestClassifyLayer:
    def test_ui_by_funcname(self):
        assert classify_layer("app", "renderComponent") == "ui"

    def test_api_by_filename(self):
        assert classify_layer("api_client", "call") == "api"

    def test_db_by_funcname(self):
        assert classify_layer("app", "query_database") == "db"

    def test_util_by_filename(self):
        assert classify_layer("formatter_utils", "format") == "util"

    def test_unknown_fallback(self):
        assert classify_layer("main", "process") == "unknown"

    def test_handler_is_ui(self):
        assert classify_layer("form", "handleSubmit") == "ui"

    def test_repository_is_db(self):
        assert classify_layer("user_repository", "find") == "db"

    def test_validator_is_util(self):
        assert classify_layer("app", "validateInput") == "util"

    def test_controller_is_api(self):
        assert classify_layer("user_controller", "index") == "api"
