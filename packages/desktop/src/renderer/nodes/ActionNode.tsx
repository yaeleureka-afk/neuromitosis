import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

interface ActionNodeData {
  label: string;
  nodeType: string;
  status: 'idle' | 'running' | 'done' | 'error';
}

export const ActionNode = memo(({ data }: NodeProps) => {
  const nodeData = data as unknown as ActionNodeData;
  const statusColors = {
    idle: 'border-gray-600',
    running: 'border-amber-500 shadow-amber-500/20 shadow-lg',
    done: 'border-green-500',
    error: 'border-red-500',
  };

  return (
    <div className={`px-4 py-3 rounded-lg bg-gray-800 border-2 ${statusColors[nodeData.status]} min-w-[160px]`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-indigo-500 border-2 border-indigo-300"
      />
      <div className="flex items-center gap-2">
        <span className="text-lg">⚡</span>
        <div>
          <div className="text-xs text-amber-400 font-mono uppercase tracking-wider">Action</div>
          <div className="text-sm text-gray-200 font-medium">{nodeData.label}</div>
        </div>
      </div>
    </div>
  );
});

ActionNode.displayName = 'ActionNode';
