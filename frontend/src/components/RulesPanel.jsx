/**
 * RulesPanel.jsx
 * フィルタルール切り替えパネル
 */

const LAYERS = ["ui", "api", "db", "util", "unknown"];
const MODES  = ["detail", "summary", "custom"];

const styles = {
  panel: {
    background: "#f8f9fa",
    border: "1px solid #dee2e6",
    borderRadius: 8,
    padding: "16px 20px",
    fontSize: 13,
    minWidth: 200,
  },
  section: {
    marginBottom: 16,
  },
  label: {
    fontWeight: 600,
    marginBottom: 8,
    display: "block",
    color: "#333",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    marginBottom: 4,
    cursor: "pointer",
  },
  badge: (layer) => ({
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: 12,
    fontSize: 11,
    fontWeight: 600,
    background: LAYER_COLORS[layer] ?? "#adb5bd",
    color: "#fff",
  }),
  modeBtn: (active) => ({
    padding: "4px 10px",
    borderRadius: 6,
    border: active ? "2px solid #2d7dd2" : "1px solid #ced4da",
    background: active ? "#e8f1fb" : "#fff",
    color: active ? "#2d7dd2" : "#555",
    cursor: "pointer",
    fontWeight: active ? 600 : 400,
    fontSize: 12,
    marginRight: 4,
  }),
  divider: {
    borderTop: "1px solid #dee2e6",
    margin: "12px 0",
  },
  resetBtn: {
    width: "100%",
    padding: "6px 0",
    borderRadius: 6,
    border: "1px solid #ced4da",
    background: "#fff",
    cursor: "pointer",
    fontSize: 12,
    color: "#666",
  },
  checkbox: {
    marginRight: 4,
  },
};

const LAYER_COLORS = {
  ui:      "#6c5ce7",
  api:     "#2d7dd2",
  db:      "#00b894",
  util:    "#e17055",
  unknown: "#95a5a6",
};

/**
 * @param {{
 *   options: object,
 *   onSetMode: (mode: string) => void,
 *   onToggleLayer: (layer: string) => void,
 *   onSetDeduplicate: (v: boolean) => void,
 *   onReset: () => void,
 * }} props
 */
export default function RulesPanel({
  options,
  onSetMode,
  onToggleLayer,
  onSetDeduplicate,
  onReset,
}) {
  const { mode, includeLayers, deduplicate } = options;

  return (
    <aside style={styles.panel}>
      {/* モード選択 */}
      <div style={styles.section}>
        <span style={styles.label}>詳細度モード</span>
        <div>
          {MODES.map((m) => (
            <button
              key={m}
              style={styles.modeBtn(mode === m)}
              onClick={() => onSetMode(m)}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div style={styles.divider} />

      {/* レイヤーフィルタ（custom モード時のみ有効） */}
      <div style={styles.section}>
        <span style={{ ...styles.label, color: mode === "custom" ? "#333" : "#aaa" }}>
          レイヤーフィルタ（custom のみ）
        </span>
        {LAYERS.map((layer) => {
          const active = !includeLayers || includeLayers.includes(layer);
          return (
            <label
              key={layer}
              style={{ ...styles.row, opacity: mode === "custom" ? 1 : 0.4 }}
            >
              <input
                type="checkbox"
                style={styles.checkbox}
                checked={active}
                disabled={mode !== "custom"}
                onChange={() => onToggleLayer(layer)}
              />
              <span style={styles.badge(layer)}>{layer}</span>
            </label>
          );
        })}
      </div>

      <div style={styles.divider} />

      {/* 重複除去 */}
      <div style={styles.section}>
        <label style={styles.row}>
          <input
            type="checkbox"
            style={styles.checkbox}
            checked={!!deduplicate}
            onChange={(e) => onSetDeduplicate(e.target.checked)}
          />
          重複呼び出しを集約
        </label>
      </div>

      <button style={styles.resetBtn} onClick={onReset}>
        ↺ リセット
      </button>
    </aside>
  );
}
