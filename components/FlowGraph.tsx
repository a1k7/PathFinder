'use client';

import React from 'react';
import { ReactFlow, Background, Controls, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 50, y: 100 }, data: { label: '🤖 Decision Agent' }, style: { background: '#1e293b', color: '#fff', border: '1px solid #475569', borderRadius: 8, padding: 10 } },
  { id: '2', position: { x: 260, y: 100 }, data: { label: '🛡️ PATHFINDER Interceptor' }, style: { background: '#0284c7', color: '#fff', border: '1px solid #38bdf8', borderRadius: 8, padding: 10 } },
  { id: '3', position: { x: 520, y: 30 }, data: { label: '📜 Policy Evaluator (YAML)' }, style: { background: '#334155', color: '#fff', border: '1px solid #3f6dac', borderRadius: 8, padding: 10 } },
  { id: '4', position: { x: 520, y: 170 }, data: { label: '🔑 RSA-PSS Signer' }, style: { background: '#059669', color: '#fff', border: '1px solid #34d399', borderRadius: 8, padding: 10 } },
  { id: '5', position: { x: 780, y: 100 }, data: { label: '📦 Verified Receipt DB' }, style: { background: '#1e293b', color: '#fff', border: '1px solid #475569', borderRadius: 8, padding: 10 } },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e3-4', source: '3', target: '4', label: 'Allow' },
  { id: 'e4-5', source: '4', target: '5', animated: true },
];

export default function FlowGraph() {
  return (
    <div className="h-64 w-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
        <Background color="#334155" gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
