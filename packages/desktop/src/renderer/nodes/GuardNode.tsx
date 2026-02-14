import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

interface GuardNodeData {
  label: string;
  nodeType: string;
  status: 'idle' | 'running' | 'done' | 'error' | 'drift';
}

export const GuardNode = memo(({ data }: NodeProps) => {
  const nodeData = data as unknown as GuardNodeData;
  const statusColors = {
    idle: 'border-gray-600',
    running: 'border-cyan-500 shadow-cyan-500/20 shadow-lg',
    done: 'border-green-500',
    error: 'border-red-500',
    drift: 'border-red-400 shadow-red-400/30 shadow-lg animate-pulse',
  };

  return (
    <div className={`px-4 py-3 rounded-lg bg-gray-900 border-2 ${statusColors[nodeData.status]} min-w-[160px]`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-cyan-500 border-2 border-cyan-300"
      />
      <div className="flex items-center gap-2">
        <span className="text-lg">🛡️</span>
        <div>
          <div className="text-xs text-cyan-400 font-mono uppercase tracking-wider">æ Guard</div>
          <div className="text-sm text-gray-200 font-medium">{nodeData.label}</div>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-purple-500 border-2 border-purple-300"
      />
    </div>
  );
});

GuardNode.displayName = 'GuardNode';
