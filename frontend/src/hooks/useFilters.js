import { useState, useCallback } from "react";
import { applySequenceFilter } from "../utils/filterEngine";

/**
 * useFilters – manage filter state and apply it to a list of CallInfo objects.
 *
 * Returns
 * -------
 * filters      : current filter settings object
 * setFilter    : (key, value) => void – update a single filter field
 * applyFilters : (calls) => CallInfo[] – apply current filters to a calls array
 * resetFilters : () => void
 */
export default function useFilters() {
  const [filters, setFilters] = useState({
    mode: "detail",
    includeLayers: [],
    excludeLayers: [],
    includeCallers: [],
    deduplicate: true,
  });

  const setFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      mode: "detail",
      includeLayers: [],
      excludeLayers: [],
      includeCallers: [],
      deduplicate: true,
    });
  }, []);

  const applyFilters = useCallback(
    (calls) => applySequenceFilter(calls, filters),
    [filters]
  );

  return { filters, setFilter, applyFilters, resetFilters };
}
