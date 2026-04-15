/**
 * layerClassifier.js – JavaScript port of the Python layer classifier.
 *
 * classifyLayer(name, filepath?) -> "UI" | "API" | "DB" | "Util" | "App"
 */

const LAYER_RULES = [
  ["UI",   /component|view|page|screen|widget|jsx|tsx|render|ui/i],
  ["API",  /api|service|client|request|http|rest|graphql|grpc|endpoint/i],
  ["DB",   /db|dao|repository|model|orm|schema|migration|database|sql|mongo|redis/i],
  ["Util", /util|helper|tool|common|shared|lib|mixin|decorator|middleware/i],
];

/**
 * Classify a module name + optional filepath into a layer label.
 *
 * @param {string} name       - module / caller name
 * @param {string} [filepath] - optional file path for extra context
 * @returns {string}
 */
export function classifyLayer(name = "", filepath = "") {
  const candidates = [name];
  if (filepath) {
    const parts = filepath.replace(/\\/g, "/").split("/");
    candidates.push(...parts);
    // also push stem without extension
    const last = parts[parts.length - 1] || "";
    const stem = last.includes(".") ? last.split(".").slice(0, -1).join(".") : last;
    if (stem) candidates.push(stem);
  }

  for (const candidate of candidates) {
    for (const [layer, pattern] of LAYER_RULES) {
      if (pattern.test(candidate)) return layer;
    }
  }
  return "App";
}
