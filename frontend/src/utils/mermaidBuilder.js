/**
 * mermaidBuilder.js
 * calls 配列から Mermaid sequenceDiagram テキストを生成する
 */

/**
 * 識別子として安全な名前に変換する
 * @param {string} name
 * @returns {string}
 */
function safeName(name) {
  return (name || "unknown").replace(/[^a-zA-Z0-9_]/g, "_");
}

/**
 * SequenceData と filtered calls から Mermaid テキストを生成する
 * @param {{ participants: string[], calls: object[] }} data
 * @param {object[]|null} calls フィルタ済み呼び出し（null の場合は data.calls を使用）
 * @returns {string}
 */
export function buildMermaid(data, calls = null) {
  const targetCalls = calls ?? data.calls ?? [];
  const lines = ["sequenceDiagram"];

  // 参加者宣言
  const participants = data.participants ?? [];
  for (const p of participants) {
    if (p && p !== "?" && p !== "") {
      lines.push(`    participant ${safeName(p)}`);
    }
  }
  lines.push("");

  // 呼び出し矢印
  for (const call of targetCalls) {
    const caller = safeName(call.caller_file ?? "unknown");
    const callee = safeName(call.callee_object ?? "unknown");
    const func   = call.callee_func ?? "";
    const note   = call.note;

    if (note) {
      lines.push(`    Note over ${caller},${callee}: ${note}`);
    }
    lines.push(`    ${caller}->>${callee}: ${func}()`);
  }

  return lines.join("\n");
}
