/**
 * SequenceDiagram.jsx
 * メインコンポーネント: Mermaid シーケンス図ビューア + ルールパネル
 * 企画書風 A4 レイアウト
 */

import { useMemo } from "react";
import { useFilters } from "../hooks/useFilters";
import { buildMermaid } from "../utils/mermaidBuilder";
import MermaidRenderer from "./MermaidRenderer";
import RulesPanel from "./RulesPanel";

// ─── A4 風スタイル ───────────────────────────────────────────
const styles = {
  page: {
    width: "100%",
    maxWidth: 1100,
    margin: "0 auto",
    padding: "32px 24px",
    fontFamily: "'Helvetica Neue', Arial, 'Hiragino Sans', sans-serif",
    color: "#2c3e50",
  },
  header: {
    borderBottom: "3px solid #2d7dd2",
    paddingBottom: 12,
    marginBottom: 24,
  },
  title: {
    fontSize: 22,
    fontWeight: 700,
    margin: 0,
    color: "#1a252f",
  },
  subtitle: {
    fontSize: 13,
    color: "#7f8c8d",
    margin: "4px 0 0",
  },
  body: {
    display: "flex",
    gap: 24,
    alignItems: "flex-start",
  },
  diagram: {
    flex: 1,
    background: "#fff",
    border: "1px solid #dee2e6",
    borderRadius: 8,
    padding: 20,
    minHeight: 300,
    overflow: "auto",
  },
  stats: {
    fontSize: 12,
    color: "#888",
    marginBottom: 12,
    display: "flex",
    gap: 12,
  },
  statBadge: {
    background: "#f1f3f5",
    borderRadius: 4,
    padding: "2px 8px",
  },
  emptyMsg: {
    textAlign: "center",
    color: "#aaa",
    padding: "60px 0",
    fontSize: 14,
  },
};

/**
 * @param {{
 *   data: { participants: string[], calls: object[], notes: object[], source_files: string[] }|null,
 *   title?: string,
 * }} props
 */
export default function SequenceDiagram({ data, title = "シーケンス図" }) {
  const rawCalls = data?.calls ?? [];

  const { filteredCalls, options, setMode, toggleLayer, setDeduplicate, resetOptions } =
    useFilters(rawCalls);

  const mermaidText = useMemo(() => {
    if (!data || filteredCalls.length === 0) return null;
    return buildMermaid(data, filteredCalls);
  }, [data, filteredCalls]);

  return (
    <div style={styles.page}>
      {/* ヘッダー */}
      <header style={styles.header}>
        <h1 style={styles.title}>{title}</h1>
        {data && (
          <p style={styles.subtitle}>
            解析ファイル数: {data.source_files?.length ?? 0} |
            参加者: {data.participants?.length ?? 0} |
            呼び出し総数: {rawCalls.length}
          </p>
        )}
      </header>

      {/* ボディ */}
      <div style={styles.body}>
        {/* ダイアグラム */}
        <section style={styles.diagram}>
          {/* 統計バッジ */}
          <div style={styles.stats}>
            <span style={styles.statBadge}>表示: {filteredCalls.length} calls</span>
            <span style={styles.statBadge}>モード: {options.mode}</span>
            {options.includeLayers && (
              <span style={styles.statBadge}>
                レイヤー: {options.includeLayers.join(", ")}
              </span>
            )}
          </div>

          {mermaidText ? (
            <MermaidRenderer text={mermaidText} />
          ) : (
            <div style={styles.emptyMsg}>
              {data ? "表示できる呼び出しがありません" : "データを読み込んでください"}
            </div>
          )}
        </section>

        {/* ルールパネル */}
        <RulesPanel
          options={options}
          onSetMode={setMode}
          onToggleLayer={toggleLayer}
          onSetDeduplicate={setDeduplicate}
          onReset={resetOptions}
        />
      </div>
    </div>
  );
}
