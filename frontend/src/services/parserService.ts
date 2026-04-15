/**
 * parserService.ts
 * Thin IPC wrapper that calls window.electronAPI methods.
 * Falls back gracefully when running outside Electron.
 */

export interface ScreenParseRequest {
  action: "parse_directory" | "parse_file" | "export_json";
  root?: string;
  file?: string;
  filter?: boolean;
}

export interface ScreenParseResponse {
  data?: unknown;
  error?: string;
}

function getAPI(): typeof window.electronAPI | null {
  if (typeof window !== "undefined" && window.electronAPI) {
    return window.electronAPI;
  }
  return null;
}

/** Send a screen-definition parse request via Electron IPC. */
export async function fetchScreenDefinition(
  request: ScreenParseRequest
): Promise<ScreenParseResponse> {
  const api = getAPI();
  if (!api || typeof api.fetchScreenDefinition !== "function") {
    return { error: "Electron IPC not available (electronAPI.fetchScreenDefinition)" };
  }
  try {
    const result = await api.fetchScreenDefinition(request);
    return { data: result };
  } catch (err) {
    return { error: String(err) };
  }
}
