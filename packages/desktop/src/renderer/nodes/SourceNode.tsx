import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

interface SourceNodeData {
  label: string;
  nodeType: string;
  status: 'idle' | 'running' | 'done' | 'error';
}

export const SourceNode = memo(({ data }: NodeProps) => {
  const nodeData = data as unknown as SourceNodeData;
  const statusColors = {
    idle: 'border-gray-600',
    running: 'border-blue-500 shadow-blue-500/20 shadow-lg',
    done: 'border-green-500',
    error: 'border-red-500',
  };

  return (
    <div className={`px-4 py-3 rounded-lg bg-gray-800 border-2 ${statusColors[nodeData.status]} min-w-[160px]`}>
      <div className="flex items-center gap-2">
        <span className="text-lg">📡</span>
        <div>
          <div className="text-xs text-purple-400 font-mono uppercase tracking-wider">Source</div>
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

SourceNode.displayName = 'SourceNode';
