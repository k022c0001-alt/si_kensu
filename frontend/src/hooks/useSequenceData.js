/**
 * useSequenceData.js
 * Electron IPC 経由で Python Sequence パーサーを呼び出すカスタムフック
 */

import { useState, useCallback } from "react";

/** 非 Electron 環境で使用するモックデータ */
const MOCK_DATA = {
  project_root: "/mock/project",
  calls: [
    { caller: "User", callee: "API", line_number: 10, file_path: "app.py", args: [], return_type: null },
    { caller: "API", callee: "Database", line_number: 20, file_path: "api.py", args: ["query"], return_type: "list" },
    { caller: "Database", callee: "API", line_number: 25, file_path: "db.py", args: [], return_type: "rows" },
    { caller: "API", callee: "User", line_number: 30, file_path: "api.py", args: [], return_type: "json" },
  ],
  config: {
    mode: "detail",
    exclude_private: false,
    exclude_builtins: true,
  },
  stats: {
    total_files: 3,
    total_calls: 4,
    filtered_calls: 4,
  },
};

/**
 * Electron IPC 経由で Python Sequence パーサーを呼び出すフック
 *
 * @returns {{
 *   data: SequenceData | null,
 *   loading: boolean,
 *   error: string | null,
 *   analyze: (rootDir: string, filterConfig?: object) => Promise<void>,
 *   updateFilter: (newFilter: object) => Promise<void>,
 * }}
 */
export default function useSequenceData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRoot, setLastRoot] = useState(null);

  const analyze = useCallback(async (rootDir, filterConfig = {}) => {
    setLoading(true);
    setError(null);
    setLastRoot(rootDir);

    try {
      const api = typeof window !== "undefined" ? window.electronAPI : null;

      if (!api || typeof api.fetchSequenceData !== "function") {
        // 非 Electron 環境ではモックデータを返す
        await new Promise((r) => setTimeout(r, 300));
        setData({ ...MOCK_DATA, project_root: rootDir || MOCK_DATA.project_root });
        return;
      }

      const request = {
        root: rootDir,
        mode: filterConfig.mode ?? "detail",
        exclude_private: filterConfig.exclude_private ?? false,
        exclude_builtins: filterConfig.exclude_builtins ?? true,
      };

      const result = await api.fetchSequenceData(request);
      setData(result?.data ?? result);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const updateFilter = useCallback(
    async (newFilter) => {
      if (!lastRoot) return;
      await analyze(lastRoot, newFilter);
    },
    [lastRoot, analyze]
  );

  return { data, loading, error, analyze, updateFilter };
}
