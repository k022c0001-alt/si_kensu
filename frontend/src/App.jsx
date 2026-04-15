/**
 * App.jsx
 * アプリケーションルートコンポーネント
 *
 * デモ: シーケンスデータを JSON で渡すか、ファイルアップロードで読み込む
 */

import { useState } from "react";
import SequenceDiagram from "./components/SequenceDiagram";

const DEMO_DATA = {
  participants: ["app", "api", "db"],
  source_files: ["app.py", "api.py", "db.py"],
  calls: [
    { caller_file: "app", caller_func: "run",      callee_object: "api", callee_func: "fetch_user",  line: 5,  layer: "api",  note: "ユーザー取得" },
    { caller_file: "api", caller_func: "fetch_user", callee_object: "db", callee_func: "query",       line: 12, layer: "db",   note: null },
    { caller_file: "api", caller_func: "fetch_user", callee_object: "db", callee_func: "close",       line: 15, layer: "db",   note: null },
    { caller_file: "app", caller_func: "run",      callee_object: "api", callee_func: "save_user",   line: 20, layer: "api",  note: "ユーザー保存" },
    { caller_file: "api", caller_func: "save_user",  callee_object: "db", callee_func: "insert",      line: 28, layer: "db",   note: null },
  ],
  notes: [],
};

const pageStyle = {
  minHeight: "100vh",
  background: "#f4f6f8",
  padding: "24px 16px",
};

const uploadCardStyle = {
  maxWidth: 1100,
  margin: "0 auto 16px",
  background: "#fff",
  border: "1px solid #dee2e6",
  borderRadius: 8,
  padding: "12px 20px",
  display: "flex",
  alignItems: "center",
  gap: 12,
  fontSize: 13,
};

export default function App() {
  const [data, setData] = useState(DEMO_DATA);
  const [loadError, setLoadError] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        setData(parsed);
        setLoadError(null);
      } catch (err) {
        setLoadError("JSON の解析に失敗しました: " + err.message);
      }
    };
    reader.readAsText(file);
  }

  return (
    <div style={pageStyle}>
      {/* ファイル読み込みバー */}
      <div style={uploadCardStyle}>
        <strong>📂 JSON 読み込み:</strong>
        <input type="file" accept=".json" onChange={handleFileChange} />
        {loadError && <span style={{ color: "red" }}>{loadError}</span>}
        <span style={{ marginLeft: "auto", color: "#888" }}>
          ※ バックエンドの出力 JSON をドロップしてください
        </span>
      </div>

      {/* シーケンス図 */}
      <SequenceDiagram data={data} title="シーケンス図ビューア" />
    </div>
  );
}
