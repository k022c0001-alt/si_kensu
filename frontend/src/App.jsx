/**
 * App.jsx
 * アプリケーションルートコンポーネント
 *
 * 3つのビューアをタブで切り替える:
 *   1. シーケンス図
 *   2. クラス図
 *   3. 画面項目定義書
 */

import { useState } from "react";
import SequenceDiagram from "./components/SequenceDiagram";
import ClassDiagramViewer from "./components/diagram/ClassDiagramViewer";
import ScreenDefinitionView from "./components/screen-definition/ScreenDefinitionView";

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

const TABS = [
  { id: "sequence", label: "📊 シーケンス図" },
  { id: "class",    label: "🏗 クラス図" },
  { id: "screen",   label: "🖥 画面項目定義書" },
];

const pageStyle = {
  minHeight: "100vh",
  background: "#f4f6f8",
  padding: "24px 16px",
};

const tabBarStyle = {
  maxWidth: 1200,
  margin: "0 auto 16px",
  display: "flex",
  gap: 4,
  borderBottom: "2px solid #dee2e6",
};

function tabStyle(active) {
  return {
    padding: "8px 20px",
    fontSize: 14,
    fontWeight: active ? 700 : 400,
    background: active ? "#fff" : "transparent",
    border: active ? "1px solid #dee2e6" : "1px solid transparent",
    borderBottom: active ? "2px solid #fff" : "none",
    borderRadius: "4px 4px 0 0",
    cursor: "pointer",
    marginBottom: -2,
    color: active ? "#1976d2" : "#555",
  };
}

const uploadCardStyle = {
  maxWidth: 1200,
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
  const [activeTab, setActiveTab] = useState("sequence");
  const [sequenceData, setSequenceData] = useState(DEMO_DATA);
  const [loadError, setLoadError] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        setSequenceData(parsed);
        setLoadError(null);
      } catch (err) {
        setLoadError("JSON の解析に失敗しました: " + err.message);
      }
    };
    reader.readAsText(file);
  }

  return (
    <div style={pageStyle}>
      {/* タブバー */}
      <div style={tabBarStyle}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            style={tabStyle(activeTab === tab.id)}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* シーケンス図タブ */}
      {activeTab === "sequence" && (
        <>
          <div style={uploadCardStyle}>
            <strong>📂 JSON 読み込み:</strong>
            <input type="file" accept=".json" onChange={handleFileChange} />
            {loadError && <span style={{ color: "red" }}>{loadError}</span>}
            <span style={{ marginLeft: "auto", color: "#888" }}>
              ※ バックエンドの出力 JSON をドロップしてください
            </span>
          </div>
          <SequenceDiagram data={sequenceData} title="シーケンス図ビューア" />
        </>
      )}

      {/* クラス図タブ */}
      {activeTab === "class" && (
        <ClassDiagramViewer root="." mode="detail" />
      )}

      {/* 画面項目定義書タブ */}
      {activeTab === "screen" && (
        <ScreenDefinitionView />
      )}
    </div>
  );
}
