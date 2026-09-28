'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Play, CheckCircle2, XCircle, ShieldAlert, Key } from 'lucide-react';

export default function HitlApproval({ onDecisionMade }: { onDecisionMade: () => void }) {
  const [user, setUser] = useState('alice');
  const [action, setAction] = useState('create');
  const [amount, setAmount] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.decide({
        user,
        action,
        amount: Number(amount),
      });
      setResult(res);
      onDecisionMade();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to communicate with decision endpoint');
    } finally {
      setLoading(false);
    }
  };

  const isAllowed = result?.allowed === true || result?.effect === 'allow';

  return (
    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-slate-100 flex flex-col gap-4">
      <div className="flex items-center gap-2 text-sky-400 font-semibold">
        <ShieldAlert className="w-5 h-5" />
        <h3>HITL / Engine Decision Gate</h3>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="text-xs text-slate-400">Actor/User</label>
          <input
            className="w-full bg-slate-800 border border-slate-700 px-3 py-1.5 rounded text-sm mt-1 focus:outline-sky-500"
            value={user}
            onChange={(e) => setUser(e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-slate-400">Action</label>
          <select
            className="w-full bg-slate-800 border border-slate-700 px-3 py-1.5 rounded text-sm mt-1 focus:outline-sky-500"
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            <option value="create">create</option>
            <option value="update">update</option>
            <option value="delete">delete</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-400">Amount ($)</label>
          <input
            type="number"
            className="w-full bg-slate-800 border border-slate-700 px-3 py-1.5 rounded text-sm mt-1 focus:outline-sky-500"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="flex gap-2">
        <button
          disabled={loading}
          onClick={handleSubmit}
          className="flex-1 bg-sky-600 hover:bg-sky-500 text-white py-2 rounded text-sm flex items-center justify-center gap-2 font-medium disabled:opacity-50 transition-colors"
        >
          <Play className="w-4 h-4" /> {loading ? 'Evaluating Policy...' : 'Evaluate Engine Decision'}
        </button>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg border border-rose-600/50 bg-rose-950/40 text-rose-200 text-xs">
          ⚠️ {errorMsg}
        </div>
      )}

      {result && (
        <div
          className={`p-4 rounded-lg border text-sm flex flex-col gap-2 ${
            isAllowed
              ? 'bg-emerald-950/30 border-emerald-600/40 text-emerald-200'
              : 'bg-rose-950/30 border-rose-600/40 text-rose-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {isAllowed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
            )}
            <span className="font-semibold uppercase tracking-wider text-xs">
              Policy Verdict: {isAllowed ? 'ALLOWED' : 'DENIED'}
            </span>
          </div>

          {result.reason && (
            <p className="text-xs text-slate-300 font-mono bg-slate-950/60 p-2 rounded">
              {result.reason}
            </p>
          )}

          {result.receipt?.signature_b64 && (
            <div className="text-xs text-slate-400 mt-1 flex flex-col gap-1">
              <span className="flex items-center gap-1 text-slate-300 font-medium">
                <Key className="w-3.5 h-3.5 text-sky-400" /> RSA-PSS Signature:
              </span>
              <p className="font-mono text-[10px] text-slate-400 break-all bg-slate-950/60 p-2 rounded border border-slate-800">
                {result.receipt.signature_b64}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
