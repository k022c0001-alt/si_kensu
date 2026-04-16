# 使用例

## 1. Sequence 図エンジン

### CLI 実行

```bash
python backend/src/main.py /path/to/project output.json
python backend/src/main.py /path/to/project output --mode summary --format mermaid
```

### Electron UI
1. アプリ起動 (`npm run dev`)
2. 「📊 シーケンス図」タブを選択
3. JSON ファイルを読み込む（バックエンド出力 JSON）
4. フィルタパネルでモード・レイヤーを切り替える

## 2. Class 図エンジン

### CLI 実行

```bash
python backend/diagram_engine/ipc/diagram_handler.py \
  '{"root":"/path/to/project","filter":{"mode":"detail"}}'
```

### Electron UI
1. アプリ起動
2. 「🏗 クラス図」タブを選択
3. Detail / Overview モードを切り替える

## 3. 画面項目定義書エンジン

### CLI 実行

```bash
python backend/screen_definition_engine/ipc/screen_handler.py \
  '{"action":"parse_directory","root":"/path/to/components"}'
```

### Electron UI
1. アプリ起動
2. 「🖥 画面項目定義書」タブを選択
3. 「ディレクトリを選択」ボタンクリック
4. React コンポーネントのディレクトリを選択
5. UI 要素一覧がテーブル表示される
6. セルをクリックして編集可能
7. 「JSON にエクスポート」で保存

## フィルタオプション

| モード | 説明 |
|--------|------|
| `detail` | 全要素・全呼び出しを表示（デフォルト） |
| `summary` | 異なるレイヤー間の呼び出しのみ表示 |
| `custom` | レイヤー・関数名で細かくフィルタ |
| `strict` | 名前・IDが揃った要素のみ表示 |
