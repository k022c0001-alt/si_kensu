# si_kensu - Intelligent Code Analysis & Visualization Engine

## 🎯 プロジェクト概要

si_kensu は、Python / JavaScript / JSX コードを自動解析して、
3種類の図を生成する Electron アプリケーションです。

### 3つの分析エンジン

1. **Sequence 図エンジン**
   - 関数呼び出しフロー分析
   - レイヤー分類（UI/API/DB/Util）

2. **Class 図エンジン**
   - クラス構造・依存関係分析
   - React コンポーネント検出

3. **画面項目定義書エンジン**
   - JSX UI 要素自動抽出
   - 編集可能なテーブル UI

## 🚀 クイックスタート

```bash
cd frontend
npm install
npm run dev
```

## 📂 ディレクトリ構成

```
si_kensu/
├── backend/
│   ├── src/                    # Sequence 図エンジン
│   ├── diagram_engine/         # Class 図エンジン
│   ├── screen_definition_engine/ # 画面定義書エンジン
│   ├── tests/                  # テスト
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/                    # React コンポーネント
│   ├── electron/               # Electron メインプロセス
│   ├── package.json
│   └── README.md
├── INSTALL.md                  # インストール手順
├── USAGE.md                    # 使用例
├── API.md                      # API リファレンス
└── README.md
```

## 📖 詳細ドキュメント

- [インストール](./INSTALL.md)
- [使用例](./USAGE.md)
- [API リファレンス](./API.md)
- [バックエンド](./backend/README.md)
- [フロントエンド](./frontend/README.md)
