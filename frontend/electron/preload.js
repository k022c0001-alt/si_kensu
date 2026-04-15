/**
 * preload.js – Electron preload script.
 *
 * Exposes a secure `window.electronAPI` object to the renderer process via
 * contextBridge.  Only the whitelisted IPC channels are accessible.
 */

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  /**
   * Fetch class diagram data from the Python backend.
   * @param {Object} request - { action, root, mode, languages }
   * @returns {Promise<Object>}
   */
  fetchDiagramData: (request) =>
    ipcRenderer.invoke("diagram:fetchData", request),

  /**
   * Generate Mermaid source for a class diagram.
   * @param {Object} request - { root, mode, languages }
   * @returns {Promise<string>}
   */
  fetchMermaid: (request) =>
    ipcRenderer.invoke("diagram:fetchMermaid", request),

  /**
   * Analyse a directory and return sequence diagram data.
   * @param {Object} request - { root, mode, includeLayers, excludeLayers }
   * @returns {Promise<Object>}
   */
  fetchSequenceData: (request) =>
    ipcRenderer.invoke("sequence:fetchData", request),

  /**
   * Parse JSX/TSX files for screen element definitions.
   * @param {Object} request - { action, root?, file?, filter? }
   * @returns {Promise<Object>}
   */
  fetchScreenDefinition: (request) =>
    ipcRenderer.invoke("screen:parse", request),
});
