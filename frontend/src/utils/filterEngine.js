/**
 * filterEngine.js
 * Python 版 sequence/filter.py と同等のフィルタロジック（フロントエンド版）
 *
 * モード:
 *   detail  – 全呼び出しを出力（デフォルト除外パターンのみ適用）
 *   summary – 異なるレイヤー間の呼び出しのみ
 *   custom  – includeLayers / excludeFuncs を指定して細かく制御
 */

const DEFAULT_EXCLUDE_PATTERNS = [
  /^__\w+__$/,                                         // __init__ などのマジックメソッド
  /^(print|len|str|int|float|bool|list|dict|set|tuple)$/, // Python ビルトイン
  /^(console|Math|JSON|Object|Array|String|Promise)$/,  // JS ビルトイン
];

/**
 * @param {string} name
 * @param {RegExp[]} patterns
 */
function matchesAny(name, patterns) {
  return patterns.some((p) => p.test(name));
}

/**
 * 呼び出し元レイヤーを全 calls から推定する
 * @param {object} call
 * @param {object[]} allCalls
 * @returns {string}
 */
function inferCallerLayer(call, allCalls) {
  const { caller_file, caller_func } = call;
  for (const c of allCalls) {
    if (c.caller_file === caller_file && c.callee_func === caller_func) {
      return c.layer ?? "unknown";
    }
  }
  return "unknown";
}

/**
 * フィルタを適用して絞り込まれた calls を返す
 *
 * @param {object[]} calls    SequenceData.calls
 * @param {object}   options
 * @param {"detail"|"summary"|"custom"} options.mode
 * @param {string[]|null}  options.includeLayers custom モード用
 * @param {string[]|null}  options.excludeFuncs  custom モード用（正規表現文字列）
 * @param {boolean}        options.deduplicate   重複除去（デフォルト: true）
 * @returns {object[]}
 */
export function applyFilter(calls, options = {}) {
  const {
    mode         = "detail",
    includeLayers = null,
    excludeFuncs  = null,
    deduplicate   = true,
  } = options;

  const excludePatterns = [
    ...DEFAULT_EXCLUDE_PATTERNS,
    ...(excludeFuncs ? excludeFuncs.map((p) => new RegExp(p)) : []),
  ];

  const seenPairs = new Set();
  const result = [];

  for (const call of calls) {
    const calleeFunc = call.callee_func ?? "";
    const layer      = call.layer ?? "unknown";

    // デフォルト除外
    if (matchesAny(calleeFunc, excludePatterns)) continue;

    // モード別フィルタ
    if (mode === "summary") {
      const callerLayer = inferCallerLayer(call, calls);
      if (callerLayer === layer) continue;
    } else if (mode === "custom") {
      if (includeLayers && !includeLayers.includes(layer)) continue;
    }

    // 重複除去
    if (deduplicate) {
      const pair = `${call.callee_object}::${calleeFunc}`;
      if (seenPairs.has(pair)) continue;
      seenPairs.add(pair);
    }

    result.push(call);
  }

  return result;
}
