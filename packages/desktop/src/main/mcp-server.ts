/**
 * Midio MCP Server
 *
 * Exposes Midio's capabilities as MCP tools.
 * This is the protocol layer — the CLI reinvented.
 *
 * Each tool here becomes:
 *   1. A callable function for Trustclaw (the agent)
 *   2. A draggable node on the canvas (the UI)
 *   3. A discoverable capability via MCP (the protocol)
 *
 * Three interfaces, one protocol. That's the thesis.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';

// Tool definitions — each maps to a Midio capability
const MIDIO_TOOLS: Tool[] = [
  // ── Loom (Runtime) ──
  {
    name: 'midio/loom.weave',
    description: 'Execute a swarm topology through the æ loom. Runs all nodes in topological order.',
    inputSchema: {
      type: 'object',
      properties: {
        loom_name: { type: 'string', description: 'Name of the loom/workflow to execute' },
        initial_inputs: { type: 'object', description: 'Initial data to feed source nodes' },
      },
      required: ['loom_name'],
    },
  },
  {
    name: 'midio/loom.getTopology',
    description: 'Return the adjacency list of the current swarm topology.',
    inputSchema: {
      type: 'object',
      properties: {
        loom_name: { type: 'string', description: 'Name of the loom to inspect' },
      },
      required: ['loom_name'],
    },
  },

  // ── Canvas (Node Management) ──
  {
    name: 'midio/canvas.addNode',
    description: 'Add a new node to the canvas. Returns the node ID.',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Node display name' },
        node_type: {
          type: 'string',
          enum: ['source', 'transform', 'action', 'guard', 'control'],
          description: 'Type of node',
        },
        position: {
          type: 'object',
          properties: { x: { type: 'number' }, y: { type: 'number' } },
          description: 'Canvas position',
        },
      },
      required: ['name', 'node_type'],
    },
  },
  {
    name: 'midio/canvas.connect',
    description: 'Wire yarn between two nodes.',
    inputSchema: {
      type: 'object',
      properties: {
        source_id: { type: 'string', description: 'Source node ID' },
        target_id: { type: 'string', description: 'Target node ID' },
        yarn_type: {
          type: 'string',
          enum: ['data', 'signal', 'state', 'guard'],
          default: 'data',
        },
      },
      required: ['source_id', 'target_id'],
    },
  },
  {
    name: 'midio/canvas.removeNode',
    description: 'Remove a node and all its connections from the canvas.',
    inputSchema: {
      type: 'object',
      properties: {
        node_id: { type: 'string', description: 'ID of the node to remove' },
      },
      required: ['node_id'],
    },
  },

  // ── Molt (Evolution) ──
  {
    name: 'midio/molt.evaluate',
    description: 'Evaluate swarm health and check if a molt is recommended.',
    inputSchema: {
      type: 'object',
      properties: {
        loom_name: { type: 'string' },
        drift_threshold: { type: 'number', default: 0.5 },
      },
      required: ['loom_name'],
    },
  },
  {
    name: 'midio/molt.execute',
    description: 'Trigger a molt — re-evaluate, rewind, re-weave the swarm.',
    inputSchema: {
      type: 'object',
      properties: {
        loom_name: { type: 'string' },
        reason: { type: 'string', description: 'Why the molt is needed' },
      },
      required: ['loom_name', 'reason'],
    },
  },

  // ── Trustclaw (Agent) ──
  {
    name: 'midio/trustclaw.chat',
    description: 'Send a message to Trustclaw and get a response.',
    inputSchema: {
      type: 'object',
      properties: {
        message: { type: 'string', description: 'User message' },
      },
      required: ['message'],
    },
  },
  {
    name: 'midio/trustclaw.status',
    description: 'Get current Trustclaw agent status — memories, skills, config.',
    inputSchema: { type: 'object', properties: {} },
  },

  // ── Memory ──
  {
    name: 'midio/memory.save',
    description: 'Save a fact or observation to persistent memory.',
    inputSchema: {
      type: 'object',
      properties: {
        content: { type: 'string', description: 'The fact to remember' },
        tags: { type: 'array', items: { type: 'string' }, description: 'Optional tags' },
      },
      required: ['content'],
    },
  },
  {
    name: 'midio/memory.search',
    description: 'Search persistent memory for relevant facts.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        max_results: { type: 'number', default: 5 },
      },
      required: ['query'],
    },
  },

  // ── Skills (Composio-backed, dynamic) ──
  {
    name: 'midio/skill.execute',
    description: 'Execute a Composio-backed skill by name. Skills are auto-discovered from connected toolkits.',
    inputSchema: {
      type: 'object',
      properties: {
        skill_name: { type: 'string', description: 'Registered skill name (e.g., fetch_unread_emails, send_email)' },
        arguments: { type: 'object', description: 'Skill-specific arguments' },
      },
      required: ['skill_name'],
    },
  },
  {
    name: 'midio/skill.list',
    description: 'List all available skills and their connection status.',
    inputSchema: { type: 'object', properties: {} },
  },
];

export class MidioMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      { name: 'midio', version: '0.1.0' },
      { capabilities: { tools: {} } }
    );

    this.registerHandlers();
  }

  private registerHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: MIDIO_TOOLS,
    }));

    // Execute a tool
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      return this.handleToolCall(name, args ?? {});
    });
  }

  private async handleToolCall(
    name: string,
    args: Record<string, unknown>
  ): Promise<{ content: Array<{ type: string; text: string }> }> {
    // Route to Python backend via JSON-RPC over stdin/stdout
    // For now, return structured stubs that show the wiring works
    console.log(`[mcp] Tool called: ${name}`, args);

    // TODO: Wire to Python child process via JSON-RPC
    // const result = await this.callPython(name, args);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            tool: name,
            status: 'stub',
            args,
            message: `Tool ${name} called successfully. Wire Python backend to execute.`,
          }),
        },
      ],
    };
  }

  // Public API for IPC calls from renderer
  async callTool(name: string, args: Record<string, unknown>) {
    return this.handleToolCall(name, args);
  }

  listTools(): Tool[] {
    return MIDIO_TOOLS;
  }

  async start(): Promise<void> {
    // For embedded use (Electron), we don't need stdio transport
    // The server is called directly via callTool/listTools
    console.log(`[mcp] Midio MCP server initialized with ${MIDIO_TOOLS.length} tools`);
  }

  // For standalone MCP server mode (e.g., Claude Desktop integration)
  async startStdio(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.log('[mcp] Midio MCP server running on stdio');
  }
}
