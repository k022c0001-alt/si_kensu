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
 * メンバー名からアクセス修飾子を自動判定する
 * __x -> - (private), _x -> # (protected), x -> + (public)
 * @param {string} name
 * @returns {string}
 */
function accessModifierFromName(name = "") {
  if (name.startsWith("__")) return "-";
  if (name.startsWith("_")) return "#";
  return "+";
}

/**
 * Python/JS ビルトイン名かどうか判定する
 * @param {string} name
 * @returns {boolean}
 */
const BUILTIN_NAMES = new Set([
  "print", "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple",
  "range", "enumerate", "zip", "map", "filter", "sorted", "reversed",
  "console", "Math", "JSON", "Object", "Array", "String", "Promise", "Number",
]);

function isBuiltin(name) {
  return BUILTIN_NAMES.has(name);
}

// ─────────────────────────────────────────────
// SequenceData (new-style) builder
// ─────────────────────────────────────────────

/**
 * 新スキーマ（SequenceData）から Mermaid sequenceDiagram テキストを生成する
 *
 * @param {import('../types').SequenceData} data
 * @param {{ mode?: string; exclude_private?: boolean; exclude_builtins?: boolean }} [filterOverride]
 * @returns {string}
 */
export function buildSequenceDiagramFromData(data, filterOverride = {}) {
  const calls = data.calls ?? [];
  const config = { ...(data.config ?? {}), ...filterOverride };
  const excludePrivate = config.exclude_private ?? false;
  const excludeBuiltins = config.exclude_builtins ?? true;
  const mode = config.mode ?? "detail";

  const filteredCalls = calls.filter((call) => {
    if (excludePrivate) {
      if ((call.caller ?? "").startsWith("_")) return false;
      if ((call.callee ?? "").startsWith("_")) return false;
    }
    if (excludeBuiltins && isBuiltin(call.callee ?? "")) return false;
    return true;
  });

  // summary モード：重複（同 caller→callee ペア）を除去
  let targetCalls = filteredCalls;
  if (mode === "summary") {
    const seen = new Set();
    targetCalls = filteredCalls.filter((call) => {
      const key = `${call.caller}→${call.callee}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  const lines = ["sequenceDiagram"];
  const participants = new Set();

  for (const call of targetCalls) {
    const caller = safeName(call.caller ?? "unknown");
    const callee = safeName(call.callee ?? caller);

    if (!participants.has(caller)) {
      lines.push(`    participant ${caller} as ${call.caller ?? caller}`);
      participants.add(caller);
    }
    if (!participants.has(callee)) {
      lines.push(`    participant ${callee} as ${call.callee ?? callee}`);
      participants.add(callee);
    }

    const argStr = (call.args ?? []).join(", ");
    const label = call.callee ? `${call.callee}(${argStr})` : `call(${argStr})`;
    lines.push(`    ${caller}->>${callee}: ${label}`);

    if (call.return_type && call.return_type !== "None" && call.return_type !== "void") {
      lines.push(`    ${callee}-->>${caller}: ${call.return_type}`);
    }
  }

  return lines.join("\n");
}

// ─────────────────────────────────────────────
// ClassDiagramData (new-style) builder
// ─────────────────────────────────────────────

/**
 * 新スキーマ（ClassDiagramData）から Mermaid classDiagram テキストを生成する
 *
 * @param {import('../types').ClassDiagramData} data
 * @param {{ mode?: string; exclude_private?: boolean; include_types?: boolean }} [filterOverride]
 * @returns {string}
 */
export function buildClassDiagramFromData(data, filterOverride = {}) {
  const classes = data.classes ?? [];
  const edges = data.edges ?? [];
  const config = { ...(data.config ?? {}), ...filterOverride };
  const excludePrivate = config.exclude_private ?? false;
  const includeTypes = config.include_types ?? true;

  const lines = ["classDiagram"];

  for (const cls of classes) {
    // ステレオタイプ
    const stereotype =
      cls.type === "function_component" || cls.type === "class_component"
        ? "<<component>>"
        : cls.type === "interface"
        ? "<<interface>>"
        : null;

    lines.push(`    class ${cls.name} {`);
    if (stereotype) {
      lines.push(`        ${stereotype}`);
    }

    for (const prop of cls.properties ?? []) {
      const sym = accessModifierFromName(prop.name);
      if (excludePrivate && sym !== "+") continue;
      const typeAnnotation = includeTypes && prop.type ? ` ${prop.type}` : "";
      const optional = prop.optional ? "?" : "";
      lines.push(`        ${sym}${prop.name}${optional}${typeAnnotation}`);
    }

    for (const method of cls.methods ?? []) {
      const sym = accessModifierFromName(method.name);
      if (excludePrivate && sym !== "+") continue;
      const params = (method.args ?? [])
        .map((a) => (includeTypes && a.type ? `${a.name} ${a.type}` : a.name))
        .join(", ");
      const retAnnotation = includeTypes && method.return_type ? ` ${method.return_type}` : "";
      const prefix = method.is_static ? "$" : method.is_async ? "*" : "";
      lines.push(`        ${sym}${prefix}${method.name}(${params})${retAnnotation}`);
    }

    lines.push("    }");
  }

  // エッジ（継承・依存関係）
  const EDGE_ARROW = {
    extends: "<|--",
    implements: "<|..",
    depends: "..>",
    association: "-->",
  };

  for (const edge of edges) {
    const arrow = EDGE_ARROW[edge.type] ?? "-->";
    if (edge.type === "extends" || edge.type === "implements") {
      lines.push(`    ${edge.to} ${arrow} ${edge.from}`);
    } else {
      lines.push(`    ${edge.from} ${arrow} ${edge.to} : ${edge.type}`);
    }
  }

  return lines.join("\n");
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
