/**
 * main_ipc.js – Electron main-process IPC handlers.
 *
 * Registers ipcMain handlers that spawn the Python backend and return
 * results to the renderer.
 */

const { ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const { registerScreenIpcHandlers } = require("./screen_ipc");

// Path to the Python interpreter (override via env for packaging)
const PYTHON = process.env.SI_KENSU_PYTHON || "python3";

// Path to the backend root (relative to this file's location)
const BACKEND_ROOT = path.resolve(__dirname, "../../backend");

/**
 * Run a Python module with JSON-encoded request piped via stdin.
 * Returns a Promise that resolves with the parsed JSON response.
 */
function callPython(modulePath, request) {
  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON, ["-m", modulePath], {
      cwd: BACKEND_ROOT,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

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

    // Send request as JSON line on stdin
    proc.stdin.write(JSON.stringify(request) + "\n");
    proc.stdin.end();
  });
}

/**
 * Register all IPC handlers.  Call this from main.js after the app is ready.
 */
function registerIpcHandlers() {
  // Class diagram – data
  ipcMain.handle("diagram:fetchData", async (_event, request) => {
    const req = { ...request, action: "parse" };
    const response = await callPython("diagram_engine.ipc.diagram_handler", req);
    return response.data ?? response;
  });

  // Class diagram – Mermaid source
  ipcMain.handle("diagram:fetchMermaid", async (_event, request) => {
    const req = { ...request, action: "mermaid" };
    const response = await callPython("diagram_engine.ipc.diagram_handler", req);
    return response.mermaid ?? "";
  });

  // Sequence diagram – data
  ipcMain.handle("sequence:fetchData", async (_event, request) => {
    const req = { ...request, action: "sequence" };
    const response = await callPython("src.main_ipc", req);
    return response.data ?? response;
  });

  // Screen definition engine
  registerScreenIpcHandlers();
}

module.exports = { registerIpcHandlers };
