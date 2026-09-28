'use client';

import { useState, useEffect } from 'react';
import FlowGraph from '@/components/FlowGraph';
import HitlApproval from '@/components/HitlApproval';
import AuditReplay from '@/components/AuditReplay';
import AgentStream from '@/components/AgentStream';
import { api } from '@/lib/api';
import { ShieldCheck, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [signal, setSignal] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleReload = async () => {
    try {
      await api.reloadPolicy();
      alert('Policies successfully reloaded from YAML without restart!');
    } catch {
      alert('Failed to reload policies.');
    }
  };

  if (!mounted) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-400 flex items-center justify-center text-sm">
        Initializing PATHFINDER Console...
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 space-y-6">
      <header className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-sky-400" />
            PATHFINDER Governance Console
          </h1>
          <p className="text-sm text-slate-400">
            Runtime Policy Enforcement, Cryptographic Audit Trail & Tamper Detection
          </p>
        </div>
        <button
          onClick={handleReload}
          className="flex items-center gap-2 bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs px-3 py-2 rounded-lg"
        >
          <RefreshCw className="w-4 h-4 text-sky-400" /> Hot Reload policies.yaml
        </button>
      </header>

      <section className="space-y-2">
        <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">
          Decision Execution Topology
        </h2>
        <FlowGraph />
      </section>

      <AgentStream onNewEvent={() => setSignal((s) => s + 1)} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HitlApproval onDecisionMade={() => setSignal((s) => s + 1)} />
        <AuditReplay refreshSignal={signal} />
      </div>
    </main>
  );
}
