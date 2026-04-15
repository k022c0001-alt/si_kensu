"""
analyzer.py
ディレクトリを再帰的に走査して複数ファイルを一括解析する
"""

import os
from pathlib import Path
from dataclasses import asdict
from typing import Optional

from ..parsers.base import SequenceData
from ..parsers.python_parser import parse_python_file
from ..parsers.javascript_parser import parse_js_file


PARSERS = {
    ".py":  parse_python_file,
    ".js":  parse_js_file,
    ".jsx": parse_js_file,
}

DEFAULT_EXCLUDE_DIRS = [
    "node_modules", "__pycache__", ".git", "dist", "build", ".venv", "venv"
]


def analyze_directory(
    root_dir: str,
    exclude_dirs: Optional[list] = None,
) -> SequenceData:
    """
    指定ディレクトリ以下の対象ファイルをすべて解析し SequenceData を返す。

    Args:
        root_dir: 解析対象のルートディレクトリ
        exclude_dirs: スキップするディレクトリ名リスト
    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    all_calls = []
    source_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 除外ディレクトリをスキップ
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in PARSERS:
                continue
            fpath = os.path.join(dirpath, fname)
            print(f"  Parsing: {fpath}")
            calls = PARSERS[ext](fpath)
            all_calls.extend(calls)
            source_files.append(fpath)

    # 参加者（participants）を重複なしで収集
    participants: set = set()
    for c in all_calls:
        participants.add(c.caller_file)
        participants.add(c.callee_object)

    return SequenceData(
        participants  = sorted(participants),
        calls         = [asdict(c) for c in all_calls],
        notes         = [asdict(c) for c in all_calls if c.note],
        source_files  = source_files,
    )
