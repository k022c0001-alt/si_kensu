# si_kensu Backend

ソースコードを解析してシーケンス図用データを生成するバックエンドモジュールです。

## ディレクトリ構成

```
backend/
├── src/                        # Sequence 図エンジン
│   ├── parsers/
│   │   ├── base.py             # 共通データ構造 (CallInfo, SequenceData)
│   │   ├── python_parser.py    # Python AST ベースパーサー
│   │   └── javascript_parser.py # JS/JSX 正規表現ベースパーサー
│   ├── layer/
│   │   └── classifier.py       # レイヤー分類 (ui/api/db/util/unknown)
│   ├── sequence/
│   │   ├── analyzer.py         # ディレクトリ走査・一括解析
│   │   └── filter.py           # フィルタエンジン (detail/summary/custom)
│   ├── output/
│   │   └── exporter.py         # JSON / Mermaid 出力
│   └── main.py                 # CLI エントリーポイント
├── diagram_engine/             # Class 図エンジン
├── screen_definition_engine/   # 画面項目定義書エンジン
│   ├── parser/                 # JSXParser / BatchJSXParser
│   ├── filter/                 # FilterRule / FilterRuleSet
│   ├── ipc/                    # screen_handler.py (Electron IPC)
│   └── __init__.py
└── tests/
    ├── test_parser.py
    ├── test_filter.py
    ├── test_layer_classifier.py
    ├── test_screen_definition.py
    ├── test_jsx_parser.py
    ├── test_filter_rules.py
    └── test_screen_handler.py
```

## セットアップ

```bash
cd backend
pip install -r requirements.txt
```

## 使い方

### Sequence 図エンジン CLI

```bash
# JSON 出力（detail モード）
python -m src.main /path/to/project output.json

# Mermaid 出力（summary モード）
python -m src.main /path/to/project output --mode summary --format mermaid
```

### 画面項目定義書エンジン CLI

```bash
python screen_definition_engine/ipc/screen_handler.py \
  '{"action":"parse_directory","root":"/path/to/components"}'
```

### Python API

```python
from screen_definition_engine.parser.jsx_parser import JSXParser

parser = JSXParser()
elements = parser.parse_file('components/UserForm.jsx')
for elem in elements:
    print(f"{elem.element_id}: {elem.name}")
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
| `.tsx` | 正規表現ベース |

## レイヤー分類

| レイヤー | 判定キーワード例 |
|---------|----------------|
| `ui`    | component, page, view, render, handle, onXxx |
| `api`   | api, fetch, axios, request, endpoint, route, controller |
| `db`    | db, dao, repository, model, query, sql, orm, session |
| `util`  | util, helper, formatter, validator, parser, converter |
| `unknown` | 上記に該当しない場合 |

## アーキテクチャ詳細

[ARCHITECTURE.md](./ARCHITECTURE.md) を参照してください。
