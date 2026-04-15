# si_kensu Frontend

Mermaid ベースのシーケンス図ビューア React アプリケーションです。

## ディレクトリ構成

```
frontend/
├── src/
│   ├── components/
│   │   ├── SequenceDiagram.jsx  # メインコンポーネント（A4 レイアウト）
│   │   ├── MermaidRenderer.jsx  # Mermaid SVG レンダラー
│   │   ├── RulesPanel.jsx       # フィルタルール切り替えパネル
│   │   └── index.js
│   ├── hooks/
│   │   ├── useFilters.js        # フィルタ状態管理
│   │   └── useMermaid.js        # Mermaid 初期化・レンダリング
│   ├── utils/
│   │   ├── filterEngine.js      # フィルタロジック（Python 版と同等）
│   │   ├── layerClassifier.js   # レイヤー分類
│   │   └── mermaidBuilder.js    # Mermaid テキスト生成
│   ├── styles/
│   │   └── SequenceDiagram.module.css
│   └── App.jsx
└── package.json
```

## セットアップ

```bash
cd frontend
npm install
npm run dev
```

## 使い方

1. `npm run dev` でローカルサーバーを起動
2. ブラウザで http://localhost:5173 にアクセス
3. バックエンドが出力した `sequence_data.json` をファイル選択から読み込む
4. ルールパネルでモード・レイヤーを切り替える

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
