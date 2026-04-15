"""
base.py
共通データ構造の定義

CallInfo: 個々の関数呼び出し情報
SequenceData: 解析結果の集合
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CallInfo:
    caller_file: str        # 呼び出し元ファイル名（拡張子なし）
    caller_func: str        # 呼び出し元関数名（トップレベルは "__module__"）
    callee_object: str      # 呼び出し先オブジェクト/クラス名（例: "api", "self"）
    callee_func: str        # 呼び出し先関数名（例: "fetch_user"）
    line: int               # ソース内の行番号
    layer: str              # レイヤー分類: "ui" / "api" / "db" / "util" / "unknown"
    note: Optional[str] = None  # 直前コメントから抽出したNote


@dataclass
class SequenceData:
    participants: list = field(default_factory=list)    # 登場するアクター一覧
    calls: list = field(default_factory=list)           # CallInfo のリスト（dict化）
    notes: list = field(default_factory=list)           # {actor, text, line} のリスト
    source_files: list = field(default_factory=list)    # 解析したファイルパス
