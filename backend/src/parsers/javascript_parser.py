"""
javascript_parser.py
JavaScript / JSX ソースファイルを正規表現で解析し、関数呼び出しを抽出する
"""

import re
from pathlib import Path
from typing import Optional

from .base import CallInfo
from ..layer.classifier import classify_layer


# 関数定義の開始を検出（function / アロー関数 / メソッド）
RE_JS_FUNC_DEF = re.compile(
    r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*\(.*?\)\s*\{)",
    re.MULTILINE
)

# 関数呼び出しを検出: obj.method(  または  method(
RE_JS_CALL = re.compile(
    r"(?:([\w$]+)\.)?([\w$]+)\s*\(",
    re.MULTILINE
)

# // コメント
RE_JS_COMMENT = re.compile(r"^\s*//\s*(.+)$")

# 除外するビルトイン・ノイズワード
JS_BUILTINS = frozenset([
    "if", "for", "while", "switch", "catch", "return", "new", "typeof",
    "console", "Math", "JSON", "Object", "Array", "String", "Promise",
    "setTimeout", "setInterval", "clearTimeout", "clearInterval",
    "parseInt", "parseFloat", "isNaN", "isFinite",
])


def parse_js_file(filepath: str) -> list:
    """正規表現でJS/JSXを解析。astほど正確ではないがシンプルに動作する。"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filename = Path(filepath).stem
    calls: list = []

    # 現在の関数スコープを簡易追跡（ブレース深度ベース）
    current_func = "__module__"
    func_stack: list = []  # (funcname, brace_depth)
    brace_depth = 0

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()

        # ── スコープ更新（波括弧カウント） ──
        open_b  = line.count("{")
        close_b = line.count("}")

        # 関数定義検出
        m = RE_JS_FUNC_DEF.search(line)
        if m and open_b > close_b:
            func_name = m.group(1) or m.group(2) or m.group(3) or "__anon__"
            func_stack.append((func_name, brace_depth))
            current_func = func_name

        brace_depth += open_b - close_b

        # スタック pop（スコープを抜けた）
        while func_stack and brace_depth <= func_stack[-1][1]:
            func_stack.pop()
        current_func = func_stack[-1][0] if func_stack else "__module__"

        # ── コメント抽出 ──
        preceding_note: Optional[str] = None
        if lineno >= 2:
            prev = lines[lineno - 2].strip()
            cm = RE_JS_COMMENT.match(prev)
            if cm:
                preceding_note = cm.group(1).strip()

        # ── 呼び出し抽出 ──
        for m in RE_JS_CALL.finditer(line):
            callee_object = m.group(1) or filename
            callee_func   = m.group(2)

            # ノイズ除去
            if callee_func in JS_BUILTINS:
                continue
            if callee_func[0].isupper():   # コンストラクタ呼び出しは除外
                continue

            layer = classify_layer(filename, callee_func)

            calls.append(CallInfo(
                caller_file   = filename,
                caller_func   = current_func,
                callee_object = callee_object,
                callee_func   = callee_func,
                line          = lineno,
                layer         = layer,
                note          = preceding_note,
            ))

    return calls
