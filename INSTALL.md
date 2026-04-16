# インストール手順

## システム要件

- Node.js 18+
- Python 3.8+
- Electron 対応 OS（macOS / Windows / Linux）

## セットアップ

### 1. 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### 2. 開発サーバー起動

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:5173 にアクセスしてください。

### 3. Electron 版ビルドと実行（オプション）

```bash
cd frontend
npm run build
npm run electron
```

## トラブルシューティング

### Python not found
- Windows: `pip` → `python -m pip`
- macOS/Linux: `python3` を使用

### npm install エラー
- キャッシュ削除: `rm -rf node_modules` + `npm install`
- Node.js バージョン確認: `node --version` (18+ 必要)

### テスト実行

```bash
# Python テスト
cd backend
pytest tests/

# React テスト
cd frontend
npm test
```
