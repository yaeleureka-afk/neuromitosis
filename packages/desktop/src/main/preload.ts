/**
 * Electron Preload — Secure bridge between renderer and main process.
 * Exposes MCP operations to the React frontend via contextBridge.
 */

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('midio', {
  // MCP tool operations
  callTool: (name: string, args: Record<string, unknown>) =>
    ipcRenderer.invoke('mcp:call-tool', name, args),

  listTools: () =>
    ipcRenderer.invoke('mcp:list-tools'),

  // App info
  version: '0.1.0',
});
