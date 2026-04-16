# si_kensu Frontend

Mermaid ベースのシーケンス図・クラス図・画面項目定義書ビューア React アプリケーションです。

## ディレクトリ構成

```
frontend/
├── src/
│   ├── components/
│   │   ├── sequence/
│   │   │   └── SequenceDiagram.jsx  # シーケンス図コンポーネント
│   │   ├── diagram/
│   │   │   └── ClassDiagramViewer.jsx # クラス図コンポーネント
│   │   ├── screen-definition/
│   │   │   ├── ScreenDefinitionTable.jsx # 編集可能テーブル
│   │   │   └── ScreenDefinitionView.jsx  # コンテナコンポーネント
│   │   ├── MermaidRenderer.jsx      # Mermaid SVG レンダラー
│   │   └── index.js
│   ├── hooks/
│   │   ├── useFilters.js           # フィルタ状態管理
│   │   ├── useMermaid.js           # Mermaid 初期化・レンダリング
│   │   ├── useDiagramData.js       # クラス図データ取得
│   │   └── useScreenDefinition.js  # 画面定義書データ管理
│   ├── services/
│   ├── types/
│   ├── styles/
│   │   └── ScreenDefinitionTable.css
│   ├── utils/
│   │   ├── filterEngine.js         # フィルタロジック
│   │   ├── layerClassifier.js      # レイヤー分類
│   │   └── mermaidBuilder.js       # Mermaid テキスト生成
│   ├── __tests__/
│   │   ├── ScreenDefinitionTable.test.jsx
│   │   ├── SequenceDiagram.test.jsx
│   │   ├── ClassDiagramViewer.test.jsx
│   │   └── App.test.jsx
│   └── App.jsx
├── electron/
│   ├── main.js                     # Electron メインプロセス
│   ├── preload.js                  # セキュアプリロード
│   └── screen_ipc.js               # 画面定義書 IPC ハンドラ
└── package.json
```

## セットアップ

```bash
cd frontend
npm install
npm run dev
```

## テスト

```bash
npm test
npm run test:coverage
```

## 使い方

1. `npm run dev` でローカルサーバーを起動
2. ブラウザで http://localhost:5173 にアクセス
3. タブでビューを切り替え
   - 📊 シーケンス図: JSON ファイルを読み込んで表示
   - 🏗 クラス図: コードのクラス構造を表示
   - 🖥 画面項目定義書: JSX から UI 要素を自動抽出

## フィルタモード

| モード | 説明 |
|--------|------|
| `detail` | 全呼び出しを表示（デフォルト） |
| `summary` | 異なるレイヤー間の呼び出しのみ表示 |
| `custom` | レイヤー・関数名で細かくフィルタ |

## 技術スタック

- React 18
- Mermaid 10
- Vite
- Jest + React Testing Library
