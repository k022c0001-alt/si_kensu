/**
 * mermaidBuilder.js – generate Mermaid diagram source strings.
 *
 * buildSequenceDiagram(calls)  -> "sequenceDiagram\n..."
 * buildClassDiagram(data)      -> "classDiagram\n..."
 */

/* ------------------------------------------------------------------ */
/* Sequence diagram                                                      */
/* ------------------------------------------------------------------ */

/**
 * @param {Array} calls - array of CallInfo objects
 * @returns {string} Mermaid sequenceDiagram source
 */
export function buildSequenceDiagram(calls = []) {
  const lines = ["sequenceDiagram"];
  const participants = new Set();

  for (const call of calls) {
    const caller = sanitize(call.caller || "App");
    const callee = sanitize(call.callee || call.caller || "App");

    if (!participants.has(caller)) {
      lines.push(`    participant ${caller}`);
      participants.add(caller);
    }
    if (!participants.has(callee)) {
      lines.push(`    participant ${callee}`);
      participants.add(callee);
    }

    lines.push(`    ${caller}->>+${callee}: ${call.function}()`);
    lines.push(`    ${callee}-->>-${caller}: return`);
  }

  return lines.join("\n");
}

/* ------------------------------------------------------------------ */
/* Class diagram                                                         */
/* ------------------------------------------------------------------ */

/**
 * @param {Object} data - ProjectData dict (from backend JSON / IPC)
 * @returns {string} Mermaid classDiagram source
 */
export function buildClassDiagram(data = {}) {
  const lines = ["classDiagram"];
  const { classes = [], components = [], dependencies = {} } = data;

  for (const cls of classes) {
    lines.push(`    class ${cls.name} {`);
    for (const prop of cls.properties || []) {
      const sym = getAccessModifier(prop.access);
      const type = prop.type ? ` ${prop.type}` : "";
      lines.push(`        ${sym}${prop.name}${type}`);
    }
    for (const method of cls.methods || []) {
      const sym = getAccessModifier(method.access);
      const params = (method.params || []).join(", ");
      const ret = method.return ? ` ${method.return}` : "";
      lines.push(`        ${sym}${method.name}(${params})${ret}`);
    }
    lines.push("    }");
  }

  for (const comp of components) {
    lines.push(`    class ${comp.name} {`);
    lines.push("        <<component>>");
    for (const prop of comp.props || []) {
      const type = prop.type ? ` ${prop.type}` : "";
      lines.push(`        +${prop.name}${type}`);
    }
    for (const hook of comp.hooks || []) {
      lines.push(`        +${hook}()`);
    }
    lines.push("    }");
  }

  // Inheritance arrows
  for (const cls of classes) {
    for (const base of cls.bases || []) {
      lines.push(`    ${base} <|-- ${cls.name}`);
    }
  }

  // Component dependency arrows (local imports only)
  for (const comp of components) {
    for (const imp of comp.imports || []) {
      if (!imp.startsWith(".")) continue;
      const depName = importToName(imp);
      if (depName) {
        lines.push(`    ${comp.name} ..> ${depName} : uses`);
      }
    }
  }

  return lines.join("\n");
}

/* ------------------------------------------------------------------ */
/* Helpers                                                               */
/* ------------------------------------------------------------------ */

/**
 * Return Mermaid access modifier symbol (+/-/#).
 * @param {string} access - "public" | "private" | "protected"
 * @returns {string}
 */
export function getAccessModifier(access = "public") {
  return { public: "+", private: "-", protected: "#" }[access] ?? "+";
}

function sanitize(name) {
  return name.replace(/[<>":]/g, "_");
}

function importToName(imp) {
  const stem = imp.replace(/\\/g, "/").split("/").pop() || "";
  const name = stem.includes(".") ? stem.split(".").slice(0, -1).join(".") : stem;
  return name && name[0] === name[0].toUpperCase() ? name : "";
}
