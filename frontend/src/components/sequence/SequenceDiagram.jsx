import React, { useEffect, useRef, useState } from "react";
import { useMermaid } from "../../hooks/useMermaid";
import { useFilters } from "../../hooks/useFilters";
import { buildSequenceDiagram } from "../../utils/mermaidBuilder";

/**
 * SequenceDiagram component
 *
 * Props
 * -----
 * calls   : Array of CallInfo objects (from backend JSON)
 * title   : optional diagram title string
 */
export default function SequenceDiagram({ calls = [], title = "Sequence Diagram" }) {
  const { filteredCalls, options: filters, setMode, toggleLayer, setDeduplicate } =
    useFilters(calls);
  const mermaidSrc = buildSequenceDiagram(filteredCalls);

  const { containerRef, error, isRendering: isLoading } = useMermaid(mermaidSrc);

  return (
    <div className="sequence-diagram-wrapper" style={styles.wrapper}>
      {/* Header / title */}
      <div style={styles.header}>
        <h2 style={styles.title}>{title}</h2>
        <span style={styles.count}>{filteredCalls.length} calls</span>
      </div>

      {/* Filter controls */}
      <FilterPanel filters={filters} setMode={setMode} toggleLayer={toggleLayer} setDeduplicate={setDeduplicate} calls={calls} />

      {/* Diagram area */}
      <div style={styles.diagramArea}>
        {isLoading && <p style={styles.hint}>Rendering…</p>}
        {error && <p style={styles.error}>⚠ {error}</p>}
        <div ref={containerRef} style={styles.mermaidContainer} />
      </div>

      {/* A4 企画書風 footer */}
      <div style={styles.footer}>
        <small>si_kensu — Sequence Diagram</small>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Filter panel                                                          */
/* ------------------------------------------------------------------ */

function FilterPanel({ filters, setMode, toggleLayer, setDeduplicate, calls }) {
  const layers = [
    ...new Set(
      calls.map((c) => c.layer ?? c.layer_caller).filter(Boolean)
    ),
  ];
  const includeLayers = filters.includeLayers ?? [];

  return (
    <div style={styles.filterPanel}>
      <label style={styles.filterLabel}>
        Mode&nbsp;
        <select
          value={filters.mode}
          onChange={(e) => setMode(e.target.value)}
          style={styles.select}
        >
          <option value="detail">Detail</option>
          <option value="summary">Summary</option>
          <option value="custom">Custom</option>
        </select>
      </label>

      {filters.mode === "custom" && (
        <div style={styles.layerToggles}>
          {layers.map((layer) => (
            <label key={layer} style={styles.checkLabel}>
              <input
                type="checkbox"
                checked={includeLayers.length === 0 || includeLayers.includes(layer)}
                onChange={() => toggleLayer(layer)}
              />
              &nbsp;{layer}
            </label>
          ))}
        </div>
      )}

      <label style={styles.filterLabel}>
        <input
          type="checkbox"
          checked={filters.deduplicate}
          onChange={(e) => setDeduplicate(e.target.checked)}
        />
        &nbsp;Deduplicate
      </label>
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
    maxWidth: 900,
    margin: "0 auto",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "2px solid #1a73e8",
    paddingBottom: 8,
    marginBottom: 16,
  },
  title: { margin: 0, fontSize: 20, color: "#1a73e8" },
  count: { fontSize: 13, color: "#888" },
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
  checkLabel: { fontSize: 13, display: "flex", alignItems: "center", gap: 4 },
  select: { marginLeft: 4, fontSize: 13 },
  layerToggles: { display: "flex", gap: 10 },
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
