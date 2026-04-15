# si_kensu Backend

ソースコードを解析してシーケンス図用データを生成するバックエンドモジュールです。

## ディレクトリ構成

```
backend/
├── src/
│   ├── parsers/
│   │   ├── base.py              # 共通データ構造 (CallInfo, SequenceData)
│   │   ├── python_parser.py     # Python AST ベースパーサー
│   │   └── javascript_parser.py # JS/JSX 正規表現ベースパーサー
│   ├── layer/
│   │   └── classifier.py        # レイヤー分類 (ui/api/db/util/unknown)
│   ├── sequence/
│   │   ├── analyzer.py          # ディレクトリ走査・一括解析
│   │   └── filter.py            # フィルタエンジン (detail/summary/custom)
│   ├── output/
│   │   └── exporter.py          # JSON / Mermaid 出力
│   └── main.py                  # CLI エントリーポイント
└── tests/
    ├── test_parser.py
    ├── test_filter.py
    └── test_layer_classifier.py
```

## セットアップ

```bash
cd backend
pip install -r requirements.txt
```

## 使い方

### CLI

```bash
# JSON 出力（detail モード）
python -m src.main /path/to/project output.json

# Mermaid 出力（summary モード）
python -m src.main /path/to/project output --mode summary --format mermaid

# custom モード（api と db レイヤーのみ、debug_ 関数を除外）
python -m src.main /path/to/project output --mode custom \
    --include-layers api db \
    --exclude-funcs "^debug_"
```

### Python API

```python
from src.sequence.analyzer import analyze_directory
from src.sequence.filter import apply_filter
from src.output.exporter import build_mermaid

# 解析
data = analyze_directory("./my_project")

# フィルタ
calls = apply_filter(data.calls, mode="summary")

# Mermaid テキスト生成
mermaid_text = build_mermaid(data, calls)
print(mermaid_text)
```

## テスト

```bash
cd backend
pytest tests/
```

## 対応言語

| 拡張子 | パーサー |
|--------|---------|
| `.py`  | Python AST（精度高） |
| `.js`  | 正規表現ベース |
| `.jsx` | 正規表現ベース |

## レイヤー分類

| レイヤー | 判定キーワード例 |
|---------|----------------|
| `ui`    | component, page, view, render, handle, onXxx |
| `api`   | api, fetch, axios, request, endpoint, route, controller |
| `db`    | db, dao, repository, model, query, sql, orm, session |
| `util`  | util, helper, formatter, validator, parser, converter |
| `unknown` | 上記に該当しない場合 |
