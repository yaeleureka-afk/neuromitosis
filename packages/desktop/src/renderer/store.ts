/**
 * Midio Store — Zustand state management
 *
 * Bridges React state with MCP tool calls.
 * Every canvas action goes through here → MCP → Python backend.
 */

import { create } from 'zustand';

interface MidioTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface MidioStore {
  // MCP tools discovered from server
  tools: MidioTool[];
  fetchTools: () => Promise<void>;
  callTool: (name: string, args: Record<string, unknown>) => Promise<unknown>;

  // Agent chat
  messages: AgentMessage[];
  sendMessage: (content: string) => Promise<void>;

  // Loom status
  isWeaving: boolean;
  lastWeaveResult: Record<string, unknown> | null;
}

export const useStore = create<MidioStore>((set, get) => ({
  tools: [],
  messages: [],
  isWeaving: false,
  lastWeaveResult: null,

  fetchTools: async () => {
    try {
      const tools = await window.midio.listTools();
      set({ tools });
    } catch (err) {
      console.error('[store] Failed to fetch tools:', err);
    }
  },

  callTool: async (name: string, args: Record<string, unknown>) => {
    try {
      const result = await window.midio.callTool(name, args);
      return result;
    } catch (err) {
      console.error(`[store] Tool ${name} failed:`, err);
      throw err;
    }
  },

  sendMessage: async (content: string) => {
    const userMsg: AgentMessage = { role: 'user', content, timestamp: Date.now() };
    set((state) => ({ messages: [...state.messages, userMsg] }));

    try {
      const result = await window.midio.callTool('midio/trustclaw.chat', { message: content });
      const text = typeof result === 'string' ? result : JSON.stringify(result);
      const assistantMsg: AgentMessage = { role: 'assistant', content: text, timestamp: Date.now() };
      set((state) => ({ messages: [...state.messages, assistantMsg] }));
    } catch {
      const errorMsg: AgentMessage = {
        role: 'assistant',
        content: '[Trustclaw unavailable — wire the LLM backend]',
        timestamp: Date.now(),
      };
      set((state) => ({ messages: [...state.messages, errorMsg] }));
    }
  },
}));
