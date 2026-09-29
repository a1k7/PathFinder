'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { History, RefreshCcw } from 'lucide-react';

export default function AuditReplay({ refreshSignal }: { refreshSignal: number }) {
  const [logs, setLogs] = useState<any[]>([]);

  const fetchLogs = async () => {
    try {
      const data = await api.getAuditLogs();
      setLogs(Array.isArray(data) ? data.slice().reverse() : []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [refreshSignal]);

  const getDecisionId = (log: any): string => {
    return log.decision_id || log.details?.decision_id || log.event_data?.decision_id || '';
  };

  const getEffect = (log: any): string => {
    if (log.effect) return log.effect;
    const details = log.details || {};
    if (details.allowed !== undefined) return details.allowed ? 'allow' : 'deny';
    if (details.replay_allowed !== undefined) return details.replay_allowed ? 'allow' : 'deny';
    return 'LOG';
  };

  const handleReplay = async (decisionId: string) => {
    if (!decisionId) {
      alert('No valid decision ID associated with this event log.');
      return;
    }
    try {
      const res = await api.replay(decisionId);
      alert(`Replay Result: Verdict is now [${res.allowed ? 'ALLOWED' : 'DENIED'}] - ${res.reason || ''}`);
      fetchLogs();
    } catch (err: any) {
      alert(`Replay failed: ${err.message}`);
    }
  };

  const handleTamperTest = async (decisionId: string) => {
    try {
      const tamperRes = await api.tamper(decisionId, 'decision_data.amount', 999999);
      alert(
        tamperRes.tamper_detected
          ? '✅ Tamper detected by backend!'
          : '❌ Tamper NOT detected — check backend fix.'
      );
    } catch (err: any) {
      alert(`Tamper test failed: ${err.message}`);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-slate-100 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold">
          <History className="w-5 h-5" />
          <h3>Audit Trail & Replay Engine</h3>
        </div>
        <button onClick={fetchLogs} className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
          <RefreshCcw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead className="bg-slate-800 text-slate-400 uppercase">
            <tr>
              <th className="p-2.5">Time</th>
              <th className="p-2.5">Decision ID</th>
              <th className="p-2.5">Action</th>
              <th className="p-2.5">Result</th>
              <th className="p-2.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.slice(0, 8).map((log, idx) => {
              const dId = getDecisionId(log);
              const effect = getEffect(log);
              return (
                <tr key={log.id || `${dId}-${idx}`} className="hover:bg-slate-800/50">
                  <td className="px-4 py-3 font-mono text-sm text-slate-300">
                    {new Date(log.timestamp.endsWith('Z') ? log.timestamp : log.timestamp + 'Z').toLocaleTimeString()}
                  </td>
                  <td className="p-2.5 font-mono text-slate-300">
                    {dId ? `${dId.slice(0, 8)}...` : 'N/A'}
                  </td>
                  <td className="p-2.5">{log.action || log.event_type || 'evaluate'}</td>
                  <td className="p-2.5">
                    <span className={`px-2 py-0.5 rounded font-mono ${effect === 'allow'
                      ? 'bg-emerald-950 text-emerald-400'
                      : effect === 'deny'
                        ? 'bg-rose-950 text-rose-400'
                        : 'bg-slate-800 text-slate-300'
                      }`}>
                      {effect.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-2.5 flex items-center gap-2">
                    <button
                      onClick={() => handleReplay(dId)}
                      disabled={!dId}
                      className="bg-indigo-600/30 hover:bg-indigo-600/60 border border-indigo-500/30 text-indigo-300 px-2 py-1 rounded disabled:opacity-30"
                    >
                      Replay
                    </button>
                    <button
                      onClick={() => handleTamperTest(dId)}
                      disabled={!dId}
                      className="bg-amber-600/30 hover:bg-amber-600/60 border border-amber-500/30 text-amber-300 px-2 py-1 rounded disabled:opacity-30"
                    >
                      Tamper
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
