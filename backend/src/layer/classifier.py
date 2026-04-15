"""
classifier.py
ファイル名と関数名からレイヤーを自動分類する
"""

import re

# レイヤー判定ルール（プロジェクトに合わせて編集可能）
LAYER_RULES = {
    "ui":   re.compile(r"(component|page|view|screen|render|handle|\bon[A-Z])", re.I),
    "api":  re.compile(r"(api|fetch|axios|request|endpoint|route|controller)", re.I),
    "db":   re.compile(r"(db|dao|repository|model|query|sql|\borm\b|session)", re.I),
    "util": re.compile(r"(util|helper|formatter|validate|validator|parser|converter)", re.I),
}


def classify_layer(filename: str, funcname: str) -> str:
    """
    ファイル名と関数名を結合したテキストに LAYER_RULES を適用してレイヤーを返す。

    Returns:
        "ui" | "api" | "db" | "util" | "unknown"
    """
    target = filename + " " + funcname
    for layer, pattern in LAYER_RULES.items():
        if pattern.search(target):
            return layer
    return "unknown"
