import { useEffect, useRef, useState } from "react";

/**
 * useMermaid – render a Mermaid diagram into a container div.
 *
 * Parameters
 * ----------
 * src : string  – Mermaid diagram source (sequenceDiagram / classDiagram).
 *
 * Returns
 * -------
 * containerRef : React ref to attach to the target <div>
 * isLoading    : boolean
 * error        : string | null
 */
export default function useMermaid(src) {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!src || !containerRef.current) return;

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    (async () => {
      try {
        // Dynamically import mermaid to avoid SSR issues
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({ startOnLoad: false, theme: "default" });

        const id = `mermaid-${Date.now()}`;
        const { svg } = await mermaid.render(id, src);

        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled) setError(String(err));
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [src]);

  return { containerRef, isLoading, error };
}
