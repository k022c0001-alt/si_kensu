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

export interface OpenDialogResult {
  canceled: boolean;
  filePaths: string[];
}

export interface SaveDialogResult {
  canceled: boolean;
  filePath?: string;
}

/** Extended electronAPI shape that includes the dialog methods. */
interface ElectronAPIWithDialogs {
  fetchScreenDefinition: (req: ScreenParseRequest) => Promise<unknown>;
  openDirectoryDialog: () => Promise<OpenDialogResult>;
  saveFileDialog: (options: Record<string, unknown>) => Promise<SaveDialogResult>;
}

function getAPI(): ElectronAPIWithDialogs | null {
  if (typeof window !== "undefined" && window.electronAPI) {
    return window.electronAPI as unknown as ElectronAPIWithDialogs;
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

/** Open a native directory picker dialog. */
export async function openDirectoryDialog(): Promise<OpenDialogResult> {
  const api = getAPI();
  if (!api || typeof api.openDirectoryDialog !== "function") {
    return { canceled: true, filePaths: [] };
  }
  try {
    return await api.openDirectoryDialog();
  } catch (err) {
    return { canceled: true, filePaths: [] };
  }
}

/** Open a native save-file dialog. */
export async function saveFileDialog(
  options?: Record<string, unknown>
): Promise<SaveDialogResult> {
  const api = getAPI();
  if (!api || typeof api.saveFileDialog !== "function") {
    return { canceled: true };
  }
  try {
    return await api.saveFileDialog(options ?? {});
  } catch (err) {
    return { canceled: true };
  }
}
