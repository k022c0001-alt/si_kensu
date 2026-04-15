/**
 * layerClassifier.js
 * ファイル名・関数名からレイヤーを自動分類する（Python 版 classifier.py と同等）
 */

const LAYER_RULES = {
  ui:   /component|page|view|screen|render|handle|\bon[A-Z]/i,
  api:  /api|fetch|axios|request|endpoint|route|controller/i,
  db:   /db|dao|repository|model|query|sql|\borm\b|session/i,
  util: /util|helper|formatter|validate|validator|parser|converter/i,
};

/**
 * ファイル名と関数名を結合してレイヤーを分類する
 * @param {string} filename
 * @param {string} funcname
 * @returns {"ui"|"api"|"db"|"util"|"unknown"}
 */
export function classifyLayer(filename, funcname) {
  const target = `${filename} ${funcname}`;
  for (const [layer, pattern] of Object.entries(LAYER_RULES)) {
    if (pattern.test(target)) return layer;
  }
  return "unknown";
}

export { LAYER_RULES };
