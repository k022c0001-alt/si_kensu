/**
 * MermaidRenderer.jsx
 * Mermaid テキストを SVG にレンダリングするシンプルなコンポーネント
 */

import { useMermaid } from "../hooks/useMermaid";

const styles = {
  container: {
    width: "100%",
    minHeight: 200,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    overflow: "auto",
  },
  error: {
    color: "#c0392b",
    background: "#fdecea",
    borderRadius: 6,
    padding: "12px 16px",
    fontSize: 13,
    fontFamily: "monospace",
    whiteSpace: "pre-wrap",
    width: "100%",
  },
  loading: {
    color: "#888",
    fontSize: 14,
  },
};

/**
 * @param {{ text: string }} props
 */
export default function MermaidRenderer({ text }) {
  const { containerRef, error, isRendering } = useMermaid(text);

  if (error) {
    return (
      <div style={styles.container}>
        <pre style={styles.error}>⚠ Mermaid エラー:{"\n"}{error}</pre>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {isRendering && <span style={styles.loading}>レンダリング中…</span>}
      <div ref={containerRef} style={{ width: "100%" }} />
    </div>
  );
}
