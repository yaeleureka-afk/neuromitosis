import React from 'react';

interface ToolbarProps {
  onAddNode: (type: 'source' | 'transform' | 'action' | 'guard') => void;
  onToggleAgent: () => void;
}

export function Toolbar({ onAddNode, onToggleAgent }: ToolbarProps) {
  return (
    <div className="flex gap-2 bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-lg px-4 py-2 shadow-xl">
      <button
        onClick={() => onAddNode('source')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-purple-900/50 hover:bg-purple-800/50 text-purple-300 text-sm transition-colors"
        title="Add Source Node"
      >
        <span>📡</span> Source
      </button>
      <button
        onClick={() => onAddNode('transform')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-indigo-900/50 hover:bg-indigo-800/50 text-indigo-300 text-sm transition-colors"
        title="Add Transform Node"
      >
        <span>⚙️</span> Transform
      </button>
      <button
        onClick={() => onAddNode('action')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-amber-900/50 hover:bg-amber-800/50 text-amber-300 text-sm transition-colors"
        title="Add Action Node"
      >
        <span>⚡</span> Action
      </button>
      <button
        onClick={() => onAddNode('guard')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-cyan-900/50 hover:bg-cyan-800/50 text-cyan-300 text-sm transition-colors"
        title="Add æ Guard Node"
      >
        <span>🛡️</span> æ Guard
      </button>

      <div className="w-px bg-gray-700 mx-1" />

      <button
        onClick={onToggleAgent}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
        title="Toggle Trustclaw Agent"
      >
        <span>🧠</span> Trustclaw
      </button>
    </div>
  );
}
