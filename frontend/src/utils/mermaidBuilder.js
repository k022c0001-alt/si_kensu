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

// ─────────────────────────────────────────────
// Class diagram support (diagram_engine integration)
// ─────────────────────────────────────────────

/**
 * Return Mermaid access modifier symbol (+/-/#).
 * @param {string} access - "public" | "private" | "protected"
 * @returns {string}
 */
export function getAccessModifier(access = "public") {
  return { public: "+", private: "-", protected: "#" }[access] ?? "+";
}

/**
 * Convert ProjectData (from backend class diagram engine) to a Mermaid classDiagram.
 * @param {Object} data - { classes, components, dependencies }
 * @returns {string}
 */
export function buildClassDiagram(data = {}) {
  const lines = ["classDiagram"];
  const { classes = [], components = [], dependencies = {} } = data;

  for (const cls of classes) {
    lines.push(`    class ${cls.name} {`);
    for (const prop of cls.properties ?? []) {
      const sym = getAccessModifier(prop.access);
      const type = prop.type ? ` ${prop.type}` : "";
      lines.push(`        ${sym}${prop.name}${type}`);
    }
    for (const method of cls.methods ?? []) {
      const sym = getAccessModifier(method.access);
      const params = (method.params ?? []).join(", ");
      const ret = method.return ? ` ${method.return}` : "";
      lines.push(`        ${sym}${method.name}(${params})${ret}`);
    }
    lines.push("    }");
  }

  for (const comp of components) {
    lines.push(`    class ${comp.name} {`);
    lines.push("        <<component>>");
    for (const prop of comp.props ?? []) {
      const type = prop.type ? ` ${prop.type}` : "";
      lines.push(`        +${prop.name}${type}`);
    }
    for (const hook of comp.hooks ?? []) {
      lines.push(`        +${hook}()`);
    }
    lines.push("    }");
  }

  // Inheritance arrows
  for (const cls of classes) {
    for (const base of cls.bases ?? []) {
      lines.push(`    ${base} <|-- ${cls.name}`);
    }
  }

  // Component dependency arrows (local imports only)
  for (const comp of components) {
    for (const imp of comp.imports ?? []) {
      if (!imp.startsWith(".")) continue;
      const stem = imp.replace(/\\/g, "/").split("/").pop() ?? "";
      const depName = stem.includes(".") ? stem.split(".").slice(0, -1).join(".") : stem;
      if (depName && depName[0] === depName[0].toUpperCase()) {
        lines.push(`    ${comp.name} ..> ${depName} : uses`);
      }
    }
  }

  return lines.join("\n");
}

/**
 * Sequence diagram builder using new-style CallInfo schema.
 * @param {Array} calls
 * @returns {string}
 */
export function buildSequenceDiagram(calls = []) {
  const lines = ["sequenceDiagram"];
  const participants = new Set();

  for (const call of calls) {
    const caller = safeName(call.caller_file ?? call.caller ?? "App");
    const callee = safeName(call.callee_object ?? call.callee ?? caller);

    if (!participants.has(caller)) {
      lines.push(`    participant ${caller}`);
      participants.add(caller);
    }
    if (!participants.has(callee)) {
      lines.push(`    participant ${callee}`);
      participants.add(callee);
    }

    const func = call.callee_func ?? call.function ?? "";
    if (call.note) {
      lines.push(`    Note over ${caller},${callee}: ${call.note}`);
    }
    lines.push(`    ${caller}->>${callee}: ${func}()`);
  }

  return lines.join("\n");
}
