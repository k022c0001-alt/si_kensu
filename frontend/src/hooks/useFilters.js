/**
 * useFilters.js
 * フィルタ設定を管理するカスタムフック
 */

import { useState, useCallback } from "react";
import { applyFilter } from "../utils/filterEngine";

const DEFAULT_OPTIONS = {
  mode: "detail",
  includeLayers: null,
  excludeFuncs: null,
  deduplicate: true,
};

/**
 * @param {object[]} rawCalls SequenceData.calls
 * @returns {{ filteredCalls, options, setMode, toggleLayer, setDeduplicate }}
 */
export function useFilters(rawCalls = []) {
  const [options, setOptions] = useState(DEFAULT_OPTIONS);

  const filteredCalls = applyFilter(rawCalls, options);

  const setMode = useCallback((mode) => {
    setOptions((prev) => ({ ...prev, mode }));
  }, []);

  const toggleLayer = useCallback((layer) => {
    setOptions((prev) => {
      const current = prev.includeLayers ?? [];
      const next = current.includes(layer)
        ? current.filter((l) => l !== layer)
        : [...current, layer];
      return { ...prev, includeLayers: next.length > 0 ? next : null };
    });
  }, []);

  const setDeduplicate = useCallback((value) => {
    setOptions((prev) => ({ ...prev, deduplicate: value }));
  }, []);

  const resetOptions = useCallback(() => {
    setOptions(DEFAULT_OPTIONS);
  }, []);

  return { filteredCalls, options, setMode, toggleLayer, setDeduplicate, resetOptions };
}
