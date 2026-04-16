/**
 * sequenceService.ts
 * Electron IPC 経由で Python Sequence パーサーを呼び出すサービス
 */

export interface CallInfo {
  caller: string;
  callee: string;
  line_number: number;
  file_path: string;
  args?: string[];
  return_type?: string | null;
}

export interface SequenceData {
  project_root: string;
  calls: CallInfo[];
  config: {
    mode: "summary" | "detail";
    exclude_private: boolean;
    exclude_builtins: boolean;
  };
  stats: {
    total_files: number;
    total_calls: number;
    filtered_calls: number;
  };
}

export interface SequenceParseParams {
  root: string;
  filter?: {
    mode?: "summary" | "detail";
    exclude_private?: boolean;
    exclude_builtins?: boolean;
  };
  extract_docstring?: boolean;
}

/** Extended electronAPI shape for sequence diagram. */
interface ElectronAPIWithSequence {
  fetchSequenceData: (request: Record<string, unknown>) => Promise<unknown>;
}

function getAPI(): ElectronAPIWithSequence | null {
  if (typeof window !== "undefined" && (window as any).electronAPI) {
    return (window as any).electronAPI as ElectronAPIWithSequence;
  }
  return null;
}

export const sequenceService = {
  /**
   * Python Sequence パーサーでプロジェクトを解析する
   *
   * @param params - { root, filter, extract_docstring }
   * @returns SequenceData
   */
  async parseProject(params: SequenceParseParams): Promise<SequenceData> {
    const api = getAPI();
    if (!api || typeof api.fetchSequenceData !== "function") {
      throw new Error("Electron IPC not available (electronAPI.fetchSequenceData)");
    }

    const request: Record<string, unknown> = {
      root: params.root,
      mode: params.filter?.mode ?? "detail",
      exclude_private: params.filter?.exclude_private ?? false,
      exclude_builtins: params.filter?.exclude_builtins ?? true,
      extract_docstring: params.extract_docstring ?? false,
    };

    const result = await api.fetchSequenceData(request);
    const data = (result as any)?.data ?? result;
    return data as SequenceData;
  },
};
