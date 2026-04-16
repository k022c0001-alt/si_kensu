# si_kensu Backend アーキテクチャ

## 概要

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
│   │   └── filter.py           # フィルタエンジン
│   ├── output/
│   │   └── exporter.py         # JSON / Mermaid 出力
│   └── main.py                 # CLI エントリーポイント
│
├── diagram_engine/             # Class 図エンジン
│   ├── parser/                 # Python / JS クラス解析
│   ├── filter/                 # クラス図フィルタ
│   ├── ipc/
│   │   └── diagram_handler.py  # Electron IPC エントリポイント
│   └── __init__.py
│
├── screen_definition_engine/   # 画面項目定義書エンジン
│   ├── parser/
│   │   ├── jsx_parser.py       # JSX 要素抽出
│   │   └── jsx_parser_batch.py # ディレクトリ一括処理
│   ├── filter/
│   │   └── filter_rules.py     # FilterRule / FilterRuleSet
│   ├── ipc/
│   │   └── screen_handler.py   # Electron IPC エントリポイント
│   └── __init__.py
│
└── tests/
    ├── __init__.py
    ├── test_parser.py           # Sequence パーサーテスト
    ├── test_filter.py           # Sequence フィルタテスト
    ├── test_layer_classifier.py # レイヤー分類テスト
    ├── test_screen_definition.py # 画面定義書エンジン統合テスト
    ├── test_jsx_parser.py       # JSXParser 詳細テスト
    ├── test_filter_rules.py     # FilterRule 詳細テスト
    └── test_screen_handler.py   # screen_handler IPC テスト
```

## データフロー

### Sequence 図エンジン

```
ソースファイル
    │
    ▼
[python_parser / javascript_parser]
    │  CallInfo オブジェクト
    ▼
[layer.classifier]
    │  layer 属性付き CallInfo
    ▼
[sequence.filter]
    │  フィルタ済み calls
    ▼
[output.exporter]
    │  JSON / Mermaid テキスト
    ▼
stdout / ファイル
```

### 画面項目定義書エンジン

```
JSX/TSX ファイル
    │
    ▼
[jsx_parser.JSXParser]
    │  UIElement オブジェクト
    ▼
[filter_rules.FilterRuleSet]
    │  フィルタ済み UIElement
    ▼
[screen_handler.handle_request]
    │  JSON レスポンス
    ▼
stdout (Electron IPC)
```

## 各エンジンの拡張方法

### 新しい要素タイプを追加する

`screen_definition_engine/parser/jsx_parser.py` の `ElementType` enum に追加:

```python
class ElementType(str, Enum):
    INPUT = "input"
    # 新タイプを追加
    DATEPICKER = "datepicker"
```

### カスタムフィルタルールを追加する

```python
from screen_definition_engine.filter.filter_rules import FilterRule, FilterRuleSet

custom_rule = FilterRule("my_rule", lambda e: e.required)
rule_set = FilterRuleSet(mode="normal")
rule_set.add_rule(custom_rule)
filtered = rule_set.apply_all(elements)
```
