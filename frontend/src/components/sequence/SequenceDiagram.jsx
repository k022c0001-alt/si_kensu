import React, { useState, useMemo } from "react";
import { useMermaid } from "../../hooks/useMermaid";
import { buildSequenceDiagramFromData } from "../../utils/mermaidBuilder";

/**
 * SequenceDiagram コンポーネント（新スキーマ対応）
 *
 * Props
 * -----
 * diagramData    : SequenceData  – Python Sequence パーサーから取得したデータ
 * title          : string        – 図タイトル（省略可）
 * onFilterChange : (config) => void  – フィルタ変更コールバック（省略可）
 */
export default function SequenceDiagram({
  diagramData = null,
  title = "Sequence Diagram",
  onFilterChange,
}) {
  const defaultConfig = diagramData?.config ?? {
    mode: "detail",
    exclude_private: false,
    exclude_builtins: true,
  };

  const [filterConfig, setFilterConfig] = useState(defaultConfig);
  const [showSource, setShowSource] = useState(false);

  const mermaidSrc = useMemo(() => {
    if (!diagramData) return "";
    return buildSequenceDiagramFromData(diagramData, filterConfig);
  }, [diagramData, filterConfig]);

  const { containerRef, error: renderError, isRendering } = useMermaid(mermaidSrc);

  function handleConfigChange(key, value) {
    const next = { ...filterConfig, [key]: value };
    setFilterConfig(next);
    onFilterChange?.(next);
  }

  const stats = diagramData?.stats;
  const calls = diagramData?.calls ?? [];

  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>{title}</h2>
          {diagramData?.project_root && (
            <p style={styles.subtitle}>{diagramData.project_root}</p>
          )}
        </div>
        {stats && (
          <div style={styles.statsBar}>
            <span style={styles.statItem}>Files: {stats.total_files}</span>
            <span style={styles.statItem}>Calls: {stats.total_calls}</span>
            <span style={styles.statItem}>Filtered: {stats.filtered_calls}</span>
          </div>
        )}
      </div>

      {/* Filter panel */}
      <div style={styles.filterPanel}>
        <label style={styles.filterLabel}>
          Mode&nbsp;
          <select
            value={filterConfig.mode}
            onChange={(e) => handleConfigChange("mode", e.target.value)}
            style={styles.select}
          >
            <option value="detail">Detail</option>
            <option value="summary">Summary</option>
          </select>
        </label>

        <label style={styles.checkLabel}>
          <input
            type="checkbox"
            checked={!!filterConfig.exclude_private}
            onChange={(e) => handleConfigChange("exclude_private", e.target.checked)}
          />
          &nbsp;Private を除外
        </label>

        <label style={styles.checkLabel}>
          <input
            type="checkbox"
            checked={!!filterConfig.exclude_builtins}
            onChange={(e) => handleConfigChange("exclude_builtins", e.target.checked)}
          />
          &nbsp;ビルトインを除外
        </label>

        <button
          style={styles.toggleBtn}
          onClick={() => setShowSource((v) => !v)}
        >
          {showSource ? "▲ Mermaid 構文を隠す" : "▼ Mermaid 構文を表示"}
        </button>
      </div>

      {/* Mermaid source toggle */}
      {showSource && (
        <pre style={styles.sourceBox}>{mermaidSrc || "（データなし）"}</pre>
      )}

      {/* Diagram area */}
      <div style={styles.diagramArea}>
        {!diagramData && (
          <div style={styles.emptyMsg}>データを読み込んでください</div>
        )}
        {diagramData && calls.length === 0 && (
          <div style={styles.emptyMsg}>表示できる呼び出しがありません</div>
        )}
        {isRendering && <p style={styles.hint}>Rendering…</p>}
        {renderError && <p style={styles.error}>⚠ {renderError}</p>}
        <div ref={containerRef} style={styles.mermaidContainer} />
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <small>si_kensu — Sequence Diagram</small>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Styles (A4 企画書風 UI)                                               */
/* ------------------------------------------------------------------ */

const styles = {
  wrapper: {
    fontFamily: "'Noto Sans JP', 'Helvetica Neue', sans-serif",
    background: "#fff",
    border: "1px solid #ccc",
    borderRadius: 4,
    padding: "24px 32px",
    maxWidth: 1100,
    margin: "0 auto",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
  },
  header: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    borderBottom: "2px solid #1a73e8",
    paddingBottom: 12,
    marginBottom: 16,
  },
  title: { margin: 0, fontSize: 20, color: "#1a73e8" },
  subtitle: { margin: "4px 0 0", fontSize: 12, color: "#888" },
  statsBar: {
    display: "flex",
    gap: 12,
    alignItems: "center",
    flexShrink: 0,
  },
  statItem: {
    fontSize: 12,
    color: "#555",
    background: "#e8f1fb",
    borderRadius: 4,
    padding: "2px 8px",
  },
  filterPanel: {
    display: "flex",
    gap: 16,
    flexWrap: "wrap",
    alignItems: "center",
    marginBottom: 16,
    padding: "8px 12px",
    background: "#f5f5f5",
    borderRadius: 4,
  },
  filterLabel: { fontSize: 13, display: "flex", alignItems: "center" },
  checkLabel: {
    fontSize: 13,
    display: "flex",
    alignItems: "center",
    gap: 4,
    cursor: "pointer",
  },
  select: { marginLeft: 4, fontSize: 13 },
  toggleBtn: {
    marginLeft: "auto",
    fontSize: 12,
    padding: "4px 10px",
    borderRadius: 4,
    border: "1px solid #ccc",
    background: "#fff",
    cursor: "pointer",
    color: "#1a73e8",
  },
  sourceBox: {
    background: "#f0f4f8",
    border: "1px solid #cce",
    borderRadius: 4,
    padding: "12px 16px",
    fontSize: 12,
    fontFamily: "monospace",
    overflowX: "auto",
    marginBottom: 16,
    whiteSpace: "pre-wrap",
    wordBreak: "break-all",
  },
  diagramArea: { minHeight: 120, position: "relative" },
  mermaidContainer: { overflowX: "auto" },
  hint: { color: "#aaa", fontSize: 13 },
  error: { color: "#d32f2f", fontSize: 13 },
  emptyMsg: { color: "#aaa", fontSize: 13, padding: "24px 0", textAlign: "center" },
  footer: {
    borderTop: "1px solid #eee",
    paddingTop: 8,
    marginTop: 16,
    textAlign: "right",
    color: "#bbb",
  },
};
