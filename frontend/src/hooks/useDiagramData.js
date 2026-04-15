import { useEffect, useState } from "react";

/**
 * useDiagramData – fetch class diagram data from the Python backend via
 * Electron IPC.
 *
 * Parameters (options object)
 * ----------
 * root      : string   – project root path
 * mode      : string   – "detail" | "overview"
 * languages : string[] – optional language filter
 *
 * Returns
 * -------
 * data      : parsed ProjectData object (or null while loading)
 * isLoading : boolean
 * error     : string | null
 * reload    : () => void – trigger a re-fetch
 */
export default function useDiagramData({ root, mode = "detail", languages }) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tick, setTick] = useState(0);

  const reload = () => setTick((t) => t + 1);

  useEffect(() => {
    if (!root) return;

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    const request = { action: "parse", root, mode, languages };

    const run = async () => {
      try {
        // window.electronAPI is exposed by preload.js
        const api = window.electronAPI;
        if (!api || typeof api.fetchDiagramData !== "function") {
          throw new Error("Electron IPC not available (electronAPI.fetchDiagramData)");
        }
        const result = await api.fetchDiagramData(request);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(String(err));
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [root, mode, JSON.stringify(languages), tick]);

  return { data, isLoading, error, reload };
}
