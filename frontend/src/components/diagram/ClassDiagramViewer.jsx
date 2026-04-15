import React, { useState } from "react";
import useMermaid from "../../hooks/useMermaid";
import useDiagramData from "../../hooks/useDiagramData";
import { buildClassDiagram } from "../../utils/mermaidBuilder";

/**
 * ClassDiagramViewer component
 *
 * Props
 * -----
 * root     : string  – project root path to analyse (passed to Electron IPC)
 * mode     : "detail" | "overview"  (default: "detail")
 * languages: string[] – optional language filter
 */
export default function ClassDiagramViewer({
  root = ".",
  mode = "detail",
  languages,
}) {
  const [currentMode, setCurrentMode] = useState(mode);

  const { data, isLoading: dataLoading, error: dataError } = useDiagramData({
    root,
    mode: currentMode,
    languages,
  });

  const mermaidSrc = data ? buildClassDiagram(data) : "";
  const { containerRef, error: renderError, isLoading: renderLoading } =
    useMermaid(mermaidSrc);

  const isLoading = dataLoading || renderLoading;
  const error = dataError || renderError;

  return (
    <div style={styles.wrapper}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>Class Diagram</h2>
        <div style={styles.controls}>
          <label style={styles.label}>
            Mode&nbsp;
            <select
              value={currentMode}
              onChange={(e) => setCurrentMode(e.target.value)}
              style={styles.select}
            >
              <option value="detail">Detail</option>
              <option value="overview">Overview</option>
            </select>
          </label>
        </div>
      </div>

      {/* Summary bar */}
      {data && (
        <div style={styles.summary}>
          <span>Classes: {data.classes?.length ?? 0}</span>
          <span>Components: {data.components?.length ?? 0}</span>
          <span>Files: {Object.keys(data.dependencies ?? {}).length}</span>
        </div>
      )}

      {/* Diagram */}
      <div style={styles.diagramArea}>
        {isLoading && <p style={styles.hint}>Loading…</p>}
        {error && <p style={styles.error}>⚠ {error}</p>}
        <div ref={containerRef} style={styles.mermaidContainer} />
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <small>si_kensu — Class Diagram</small>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Styles                                                                */
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
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "2px solid #388e3c",
    paddingBottom: 8,
    marginBottom: 12,
  },
  title: { margin: 0, fontSize: 20, color: "#388e3c" },
  controls: { display: "flex", gap: 12, alignItems: "center" },
  label: { fontSize: 13, display: "flex", alignItems: "center" },
  select: { marginLeft: 4, fontSize: 13 },
  summary: {
    display: "flex",
    gap: 24,
    fontSize: 13,
    color: "#555",
    marginBottom: 12,
    padding: "6px 10px",
    background: "#f1f8e9",
    borderRadius: 4,
  },
  diagramArea: { minHeight: 120, position: "relative" },
  mermaidContainer: { overflowX: "auto" },
  hint: { color: "#aaa", fontSize: 13 },
  error: { color: "#d32f2f", fontSize: 13 },
  footer: {
    borderTop: "1px solid #eee",
    paddingTop: 8,
    marginTop: 16,
    textAlign: "right",
    color: "#bbb",
  },
};
