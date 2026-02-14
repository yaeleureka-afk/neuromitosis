/**
 * Type declarations for the Midio bridge exposed via preload.
 */

interface MidioAPI {
  callTool: (name: string, args: Record<string, unknown>) => Promise<unknown>;
  listTools: () => Promise<Array<{
    name: string;
    description: string;
    inputSchema: Record<string, unknown>;
  }>>;
  version: string;
}

declare global {
  interface Window {
    midio: MidioAPI;
  }
}

export {};
