/**
 * Midio Desktop — Electron Main Process
 *
 * Spawns the MCP server, creates the browser window,
 * and bridges the renderer to the Python backend.
 */

import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { MidioMCPServer } from './mcp-server';

let mainWindow: BrowserWindow | null = null;
let mcpServer: MidioMCPServer | null = null;
let pythonProcess: ChildProcess | null = null;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'Midio — æ loom',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // In dev, load from Vite dev server; in prod, load built files
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonBackend(): void {
  // Spawn the Python process that runs Midio core + Trustclaw
  pythonProcess = spawn('python', ['-m', 'midio.bridge'], {
    cwd: path.join(__dirname, '../../../core'),
    env: { ...process.env },
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  pythonProcess.stdout?.on('data', (data: Buffer) => {
    console.log('[python]', data.toString().trim());
  });

  pythonProcess.stderr?.on('data', (data: Buffer) => {
    console.error('[python:err]', data.toString().trim());
  });

  pythonProcess.on('exit', (code: number | null) => {
    console.log(`[python] exited with code ${code}`);
  });
}

async function startMCPServer(): Promise<void> {
  mcpServer = new MidioMCPServer();
  await mcpServer.start();
  console.log('[mcp] Server started');
}

// IPC: Renderer calls MCP tools through the main process
ipcMain.handle('mcp:call-tool', async (_event, toolName: string, args: Record<string, unknown>) => {
  if (!mcpServer) throw new Error('MCP server not initialized');
  return mcpServer.callTool(toolName, args);
});

ipcMain.handle('mcp:list-tools', async () => {
  if (!mcpServer) throw new Error('MCP server not initialized');
  return mcpServer.listTools();
});

// App lifecycle
app.whenReady().then(async () => {
  startPythonBackend();
  await startMCPServer();
  createWindow();
});

app.on('window-all-closed', () => {
  pythonProcess?.kill();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
