import React from 'react';
import { DailySnapshot } from '../../types';
import { StatusBadge, StreakBadge } from '../ui/Badge';
import { Calendar } from 'lucide-react';

interface CreativeSnapshotTableProps {
  snapshots: DailySnapshot[];
  isLoading: boolean;
}

export const CreativeSnapshotTable: React.FC<CreativeSnapshotTableProps> = ({
  snapshots,
  isLoading,
}) => {
  if (isLoading) {
    return <div className="p-6 text-center text-xs text-slate-400 font-mono">Loading snapshots...</div>;
  }

  if (snapshots.length === 0) {
    return <div className="p-6 text-center text-xs text-slate-500 font-mono">No daily snapshots recorded yet.</div>;
  }

  return (
    <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl overflow-hidden shadow-xl backdrop-blur-md">
      <div className="px-5 py-3.5 border-b border-slate-800 bg-[#111827]/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-amber-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Immutable Daily Snapshots History
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          {snapshots.length} Daily Records
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 bg-slate-900/40">
              <th className="py-2.5 px-4">Date</th>
              <th className="py-2.5 px-3 text-right">Spend</th>
              <th className="py-2.5 px-3 text-right">Revenue</th>
              <th className="py-2.5 px-3 text-right">Purchases</th>
              <th className="py-2.5 px-3 text-right">ROAS</th>
              <th className="py-2.5 px-3 text-right">CTR</th>
              <th className="py-2.5 px-3 text-right">CPA</th>
              <th className="py-2.5 px-3 text-center">Status</th>
              <th className="py-2.5 px-4 text-center">Streak</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40 text-xs font-mono">
            {snapshots.map((s) => (
              <tr key={s._id || s.date} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 px-4 font-bold text-slate-200">{s.date}</td>
                <td className="py-2.5 px-3 text-right text-slate-300 font-semibold">${s.spend.toFixed(2)}</td>
                <td className="py-2.5 px-3 text-right text-slate-300 font-semibold">${s.revenue.toFixed(2)}</td>
                <td className="py-2.5 px-3 text-right text-slate-300">{s.purchases}</td>
                <td className="py-2.5 px-3 text-right font-bold text-emerald-400">{s.roas.toFixed(2)}x</td>
                <td className="py-2.5 px-3 text-right text-slate-300">{s.ctr.toFixed(2)}%</td>
                <td className="py-2.5 px-3 text-right text-slate-300">${s.cpa.toFixed(2)}</td>
                <td className="py-2.5 px-3 text-center">
                  <StatusBadge status={s.status} />
                </td>
                <td className="py-2.5 px-4 text-center">
                  <StreakBadge streak={s.streak} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
