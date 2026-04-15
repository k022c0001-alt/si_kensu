/**
 * filterEngine.js – JavaScript port of the Python SequenceFilter.
 *
 * applySequenceFilter(calls, filters) -> CallInfo[]
 *
 * filters shape:
 * {
 *   mode           : "detail" | "summary" | "custom",
 *   includeLayers  : string[],
 *   excludeLayers  : string[],
 *   includeCallers : string[],
 *   deduplicate    : boolean,
 * }
 */

export function applySequenceFilter(calls, filters = {}) {
  const {
    mode = "detail",
    includeLayers = [],
    excludeLayers = [],
    includeCallers = [],
    deduplicate = true,
  } = filters;

  let result = [...calls];

  if (mode === "summary") {
    result = summarize(result);
  } else if (mode === "custom") {
    result = applyLayerFilter(result, includeLayers, excludeLayers);
  }

  if (includeCallers.length > 0) {
    const callerSet = new Set(includeCallers);
    result = result.filter((c) => callerSet.has(c.caller));
  }

  if (deduplicate) {
    result = deduplicated(result);
  }

  return result;
}

function summarize(calls) {
  const seen = new Set();
  return calls.filter((c) => {
    const key = `${c.caller}::${c.function}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function applyLayerFilter(calls, include, exclude) {
  const incSet = include.length > 0 ? new Set(include) : null;
  const excSet = new Set(exclude);
  return calls.filter((c) => {
    if (incSet && !incSet.has(c.layer_caller)) return false;
    if (excSet.has(c.layer_caller) || excSet.has(c.layer_callee)) return false;
    return true;
  });
}

function deduplicated(calls) {
  const seen = new Set();
  return calls.filter((c) => {
    const key = `${c.caller}::${c.callee}::${c.function}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
