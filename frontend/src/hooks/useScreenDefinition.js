/**
 * useScreenDefinition.js
 *
 * Custom hook: manage screen definition state and IPC calls.
 *
 * Returns
 * -------
 * data        – ParseDirectoryResult | null
 * isLoading   – boolean
 * error       – string | null
 * parseDirectory(root: string) – trigger a directory parse
 * parseFile(file: string)      – trigger a single-file parse
 * exportJSON()                 – re-fetch with export_json action
 * reset()                      – clear state
 */

import { useState, useCallback } from "react";

export default function useScreenDefinition() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const _call = useCallback(async (request) => {
    setIsLoading(true);
    setError(null);

    try {
      const api = window.electronAPI;
      if (!api || typeof api.fetchScreenDefinition !== "function") {
        throw new Error("Electron IPC not available (electronAPI.fetchScreenDefinition)");
      }
      const result = await api.fetchScreenDefinition(request);
      setData(result);
    } catch (err) {
      setError(String(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const parseDirectory = useCallback(
    (root) => _call({ action: "parse_directory", root, filter: true }),
    [_call]
  );

  const parseFile = useCallback(
    (file) => _call({ action: "parse_file", file, filter: true }),
    [_call]
  );

  const exportJSON = useCallback(
    (root) => _call({ action: "export_json", root, filter: true }),
    [_call]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { data, isLoading, error, parseDirectory, parseFile, exportJSON, reset };
}
