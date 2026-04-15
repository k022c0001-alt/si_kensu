/**
 * ScreenDefinitionView.jsx
 *
 * Container component: directory/file selection, parse trigger,
 * table display, and JSON/CSV export.
 */

import React, { useState, useCallback } from "react";
import useScreenDefinition from "../../hooks/useScreenDefinition";
import ScreenDefinitionTable from "./ScreenDefinitionTable";

// ── Helpers ───────────────────────────────────────────────────────────

/** Flatten ParseDirectoryResult into TableRow[]. */
function toTableRows(data) {
  if (!data) return [];
  const files = data.files ?? (data.file ? [data] : []);
  const rows = [];
  let rowIndex = 0;
  for (const fileEntry of files) {
    const filePath = fileEntry.file ?? "";
    for (const elem of fileEntry.elements ?? []) {
      const handlers = Object.entries(elem.event_handlers ?? {})
        .map(([k, v]) => `${k}:${v}`)
        .join(", ");
      rows.push({
        id: String(rowIndex++),
        file: filePath,
        element_id: elem.element_id ?? "",
        name: elem.name ?? "",
        type: elem.type ?? "",
        component_type: elem.component_type ?? "unknown",
        required: elem.required ?? false,
        max_length: elem.max_length != null ? String(elem.max_length) : "",
        placeholder: elem.placeholder ?? "",
        default_value: elem.default_value ?? "",
        event_handlers: handlers,
        comment: elem.comment ?? "",
        line_number: elem.line_number ?? 0,
      });
    }
  }
  return rows;
}

/** Export rows as JSON and trigger browser download. */
function downloadJSON(rows) {
  const blob = new Blob([JSON.stringify(rows, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "screen_definition.json";
  a.click();
  URL.revokeObjectURL(url);
}

/** Export rows as CSV and trigger browser download. */
function downloadCSV(rows) {
  if (rows.length === 0) return;
  const headers = Object.keys(rows[0]).filter((k) => k !== "id");
  const escapeCsvValue = (v) => `"${String(v).replace(/"/g, '""')}"`;
  const lines = [
    headers.map(escapeCsvValue).join(","),
    ...rows.map((r) => headers.map((h) => escapeCsvValue(r[h] ?? "")).join(",")),
  ];
  const blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "screen_definition.csv";
  a.click();
  URL.revokeObjectURL(url);
}

// ── Component ─────────────────────────────────────────────────────────

export default function ScreenDefinitionView() {
  const { data, isLoading, error, parseDirectory, parseFile, reset } =
    useScreenDefinition();

  const [rootInput, setRootInput] = useState("");
  const [fileInput, setFileInput] = useState("");
  const [rows, setRows] = useState([]);

  // Sync rows when data changes
  React.useEffect(() => {
    setRows(toTableRows(data));
  }, [data]);

  const handleSelectDirectory = useCallback(async () => {
    const api = window.electronAPI;
    if (api && typeof api.openDirectoryDialog === "function") {
      const result = await api.openDirectoryDialog();
      if (!result.canceled && result.filePaths.length > 0) {
        const dirPath = result.filePaths[0];
        setRootInput(dirPath);
        parseDirectory(dirPath);
      }
    }
  }, [parseDirectory]);

  const handleParseDirectory = useCallback(() => {
    if (rootInput.trim()) parseDirectory(rootInput.trim());
  }, [rootInput, parseDirectory]);

  const handleParseFile = useCallback(() => {
    if (fileInput.trim()) parseFile(fileInput.trim());
  }, [fileInput, parseFile]);

  const handleReset = useCallback(() => {
    reset();
    setRows([]);
    setRootInput("");
    setFileInput("");
  }, [reset]);

  const totalElements = rows.length;

  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>🖥 画面項目定義書</h2>
        {data && (
          <span style={styles.badge}>{totalElements} 件</span>
        )}
      </div>

      {/* Controls */}
      <div style={styles.controls}>
        {/* Directory parse */}
        <div style={styles.row}>
          <input
            style={styles.input}
            type="text"
            placeholder="ディレクトリパス（例: /path/to/src）"
            value={rootInput}
            onChange={(e) => setRootInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleParseDirectory()}
          />
          <button
            style={styles.btn}
            onClick={handleSelectDirectory}
            disabled={isLoading}
            title="フォルダ選択ダイアログを開く"
          >
            📁 参照
          </button>
          <button style={styles.btn} onClick={handleParseDirectory} disabled={isLoading}>
            📂 ディレクトリ解析
          </button>
        </div>

        {/* Single file parse */}
        <div style={styles.row}>
          <input
            style={styles.input}
            type="text"
            placeholder="ファイルパス（例: /path/to/Component.jsx）"
            value={fileInput}
            onChange={(e) => setFileInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleParseFile()}
          />
          <button style={styles.btn} onClick={handleParseFile} disabled={isLoading}>
            📄 ファイル解析
          </button>
        </div>

        {/* Export / Reset */}
        <div style={styles.row}>
          <button
            style={styles.btn}
            onClick={() => downloadJSON(rows)}
            disabled={rows.length === 0}
          >
            ⬇ JSON
          </button>
          <button
            style={styles.btn}
            onClick={() => downloadCSV(rows)}
            disabled={rows.length === 0}
          >
            ⬇ CSV
          </button>
          <button style={{ ...styles.btn, marginLeft: "auto" }} onClick={handleReset}>
            🔄 リセット
          </button>
        </div>
      </div>

      {/* Status */}
      {isLoading && <p style={styles.hint}>解析中…</p>}
      {error && <p style={styles.error}>⚠ {error}</p>}

      {/* Table */}
      {rows.length > 0 && (
        <div style={styles.tableArea}>
          <ScreenDefinitionTable rows={rows} onChange={setRows} />
        </div>
      )}

      {/* Footer */}
      <div style={styles.footer}>
        <small>si_kensu — 画面項目定義書エンジン</small>
      </div>
    </div>
  );
}

/* ── Styles ──────────────────────────────────────────────────────────── */

const styles = {
  wrapper: {
    fontFamily: "'Noto Sans JP', 'Helvetica Neue', sans-serif",
    background: "#fff",
    border: "1px solid #ccc",
    borderRadius: 4,
    padding: "24px 32px",
    maxWidth: 1200,
    margin: "0 auto",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    borderBottom: "2px solid #1976d2",
    paddingBottom: 8,
    marginBottom: 16,
  },
  title: { margin: 0, fontSize: 20, color: "#1976d2" },
  badge: {
    background: "#e3f2fd",
    color: "#1565c0",
    borderRadius: 10,
    padding: "2px 10px",
    fontSize: 12,
    fontWeight: 600,
  },
  controls: { display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 },
  row: { display: "flex", gap: 8, alignItems: "center" },
  input: {
    flex: 1,
    padding: "6px 10px",
    border: "1px solid #bbb",
    borderRadius: 4,
    fontSize: 13,
  },
  btn: {
    padding: "6px 14px",
    border: "1px solid #aaa",
    borderRadius: 4,
    background: "#fff",
    cursor: "pointer",
    fontSize: 13,
    whiteSpace: "nowrap",
  },
  tableArea: { overflowX: "auto", marginBottom: 16 },
  hint: { color: "#888", fontSize: 13 },
  error: { color: "#d32f2f", fontSize: 13 },
  footer: {
    borderTop: "1px solid #eee",
    paddingTop: 8,
    marginTop: 8,
    textAlign: "right",
    color: "#bbb",
  },
};
