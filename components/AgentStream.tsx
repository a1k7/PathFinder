'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Bot, Play, Square } from 'lucide-react';

export default function AgentStream({ onNewEvent }: { onNewEvent: () => void }) {
  const [isRunning, setIsRunning] = useState(false);
  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null);

  const startSimulatedEngine = () => {
    setIsRunning(true);
    const id = setInterval(async () => {
      const actions = ['create', 'update', 'delete'];
      const users = ['alice', 'bob', 'blocked_user', 'charlie'];
      const randomAction = actions[Math.floor(Math.random() * actions.length)];
      const randomUser = users[Math.floor(Math.random() * users.length)];
      const randomAmount = Math.floor(Math.random() * 2000);

      try {
        await api.decide({
          action: randomAction,
          user: randomUser,
          amount: randomAmount,
        });
        onNewEvent();
      } catch (err) {
        console.error('Agent stream failure', err);
      }
    }, 2500);

    setIntervalId(id);
  };

  const stopSimulatedEngine = () => {
    if (intervalId) clearInterval(intervalId);
    setIsRunning(false);
    setIntervalId(null);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl text-slate-100 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Bot className={`w-6 h-6 ${isRunning ? 'text-emerald-400 animate-pulse' : 'text-slate-400'}`} />
        <div>
          <h3 className="font-semibold text-sm">Autonomous Engine Simulator (`inde_client.py`)</h3>
          <p className="text-xs text-slate-400">Emulates continuous automated agent decision streams against the governance pipeline.</p>
        </div>
      </div>

      <button
        onClick={isRunning ? stopSimulatedEngine : startSimulatedEngine}
        className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
          isRunning 
            ? 'bg-rose-600/20 border border-rose-500/40 text-rose-300 hover:bg-rose-600/30' 
            : 'bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-600/30'
        }`}
      >
        {isRunning ? <Square className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
        {isRunning ? 'Stop Agent Traffic' : 'Simulate Agent Traffic'}
      </button>
    </div>
  );
}
