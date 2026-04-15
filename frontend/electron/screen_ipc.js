/**
 * screen_ipc.js – Electron IPC handlers for the Screen Definition engine.
 *
 * Call registerScreenIpcHandlers() from main_ipc.js.
 */

const { ipcMain, dialog } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

const PYTHON = process.env.SI_KENSU_PYTHON || "python3";
const BACKEND_ROOT = path.resolve(__dirname, "../../backend");

function callScreenPython(request) {
  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON, ["-m", "screen_definition_engine.ipc.screen_handler"], {
      cwd: BACKEND_ROOT,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    proc.stderr.on("data", (chunk) => { stderr += chunk.toString(); });

    proc.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`Python exited ${code}: ${stderr.trim()}`));
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (err) {
        reject(new Error(`JSON parse error: ${err.message}\nOutput: ${stdout.slice(0, 500)}`));
      }
    });

    proc.on("error", (err) => reject(err));

    proc.stdin.write(JSON.stringify(request) + "\n");
    proc.stdin.end();
  });
}

function registerScreenIpcHandlers() {
  ipcMain.handle("screen:parse", async (_event, request) => {
    const response = await callScreenPython(request);
    return response.data ?? response;
  });

  ipcMain.handle("open-directory-dialog", async (_event) => {
    const result = await dialog.showOpenDialog({
      properties: ["openDirectory"],
      title: "フォルダを選択",
    });
    return result;
  });

  ipcMain.handle("save-file-dialog", async (_event, options) => {
    const result = await dialog.showSaveDialog(options ?? {});
    return result;
  });
}

module.exports = { registerScreenIpcHandlers };
