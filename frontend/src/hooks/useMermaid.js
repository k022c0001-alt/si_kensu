/**
 * useMermaid.js
 * Mermaid ライブラリの初期化と SVG レンダリングを管理するカスタムフック
 */

import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

let mermaidInitialized = false;

function initMermaid() {
  if (!mermaidInitialized) {
    mermaid.initialize({
      startOnLoad: false,
      theme: "default",
      securityLevel: "loose",
      sequence: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 80,
        width: 150,
        height: 65,
      },
    });
    mermaidInitialized = true;
  }
}

/**
 * Mermaid テキストから SVG を生成するフック
 *
 * @param {string} mermaidText
 * @returns {{ svgRef: React.RefObject, error: string|null, isRendering: boolean }}
 */
export function useMermaid(mermaidText) {
  const containerRef = useRef(null);
  const [error, setError] = useState(null);
  const [isRendering, setIsRendering] = useState(false);

  useEffect(() => {
    if (!mermaidText || !containerRef.current) return;

    let cancelled = false;

    const render = async () => {
      setIsRendering(true);
      setError(null);

      try {
        initMermaid();
        const id = `mermaid-${Date.now()}`;
        const { svg } = await mermaid.render(id, mermaidText);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message ?? "Mermaid render error");
          if (containerRef.current) {
            containerRef.current.innerHTML = "";
          }
        }
      } finally {
        if (!cancelled) setIsRendering(false);
      }
    };

    render();
    return () => { cancelled = true; };
  }, [mermaidText]);

  return { containerRef, error, isRendering };
}
