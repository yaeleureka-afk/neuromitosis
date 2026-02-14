import React, { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { nodeTypes } from './nodes';
import { useStore } from './store';
import { Toolbar } from './components/Toolbar';
import { AgentPanel } from './components/AgentPanel';

const initialNodes: Node[] = [
  {
    id: 'welcome',
    type: 'midioSource',
    position: { x: 250, y: 200 },
    data: {
      label: 'Welcome to Midio',
      nodeType: 'source',
      status: 'idle',
    },
  },
];

export function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [agentPanelOpen, setAgentPanelOpen] = useState(false);
  const { tools, fetchTools } = useStore();

  useEffect(() => {
    fetchTools();
  }, [fetchTools]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...connection,
            animated: true,
            style: { stroke: '#a78bfa', strokeWidth: 2 },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  return (
    <div className="h-screen w-screen bg-gray-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gray-950"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#1e293b"
        />
        <Controls className="bg-gray-800 border-gray-700" />
        <MiniMap
          className="bg-gray-900 border-gray-700"
          nodeColor="#6d28d9"
          maskColor="rgba(0, 0, 0, 0.7)"
        />

        {/* Top toolbar */}
        <Panel position="top-center">
          <Toolbar
            onAddNode={(type) => {
              const id = `node-${Date.now()}`;
              setNodes((nds) => [
                ...nds,
                {
                  id,
                  type: `midio${type.charAt(0).toUpperCase() + type.slice(1)}`,
                  position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
                  data: { label: `New ${type}`, nodeType: type, status: 'idle' },
                },
              ]);
            }}
            onToggleAgent={() => setAgentPanelOpen(!agentPanelOpen)}
          />
        </Panel>

        {/* Trustclaw chat panel */}
        <Panel position="top-right">
          {agentPanelOpen && (
            <AgentPanel onClose={() => setAgentPanelOpen(false)} />
          )}
        </Panel>
      </ReactFlow>
    </div>
  );
}
