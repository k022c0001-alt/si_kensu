# API リファレンス

## Python パーサー API

### JSXParser

```python
from screen_definition_engine.parser.jsx_parser import JSXParser

parser = JSXParser()
elements = parser.parse_file('components/UserForm.jsx')

for elem in elements:
    print(f"{elem.element_id}: {elem.name} ({elem.component_type})")
```

### BatchJSXParser

```python
from screen_definition_engine.parser.jsx_parser_batch import BatchJSXParser

batch = BatchJSXParser()
result = batch.parse_directory('/path/to/components')
# result: { "RelativePath.jsx": [element_dict, ...], ... }
```

### FilterRule / FilterRuleSet

```python
from screen_definition_engine.filter.filter_rules import FilterRule, FilterRuleSet, apply_all

# デフォルトフィルタ
filtered = apply_all(elements)

# カスタムルール
rule = FilterRule("required_only", lambda e: e.required)
rule_set = FilterRuleSet(mode="strict")
rule_set.add_rule(rule)
filtered = rule_set.apply_all(elements)
```

## Electron IPC API

### screen_definition: parseDirectory

```javascript
const result = await window.electronAPI.fetchScreenDefinition({
  action: 'parse_directory',
  root: '/path/to/components',
  filter: true,
});
```

### screen_definition: parseFile

```javascript
const result = await window.electronAPI.fetchScreenDefinition({
  action: 'parse_file',
  file: '/path/to/Component.jsx',
  filter: true,
});
```

## React Hook API

### useScreenDefinition

```javascript
import useScreenDefinition from './hooks/useScreenDefinition';

const { data, isLoading, error, parseDirectory, parseFile, exportJSON, reset } = useScreenDefinition();

// ディレクトリ解析
await parseDirectory('/path/to/components');
```

### useFilters

```javascript
import { useFilters } from './hooks/useFilters';

const { filteredCalls, options, setMode, toggleLayer, setDeduplicate } = useFilters(calls);
```

### useDiagramData

```javascript
import useDiagramData from './hooks/useDiagramData';

const { data, isLoading, error } = useDiagramData({ root: '.', mode: 'detail' });
```

## UIElement データ型

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `element_id` | string | HTML id 属性 |
| `name` | string | HTML name 属性 |
| `type` | string | HTML type 属性（text, email, …） |
| `component_type` | ElementType | input / button / select / … |
| `required` | bool | 必須フラグ |
| `max_length` | int \| null | maxLength 属性 |
| `placeholder` | string | placeholder 属性 |
| `default_value` | string | defaultValue 属性 |
| `event_handlers` | dict | { "onChange": "handler", … } |
| `comment` | string | 直前のコメント |
| `line_number` | int | ソースファイル行番号 |
