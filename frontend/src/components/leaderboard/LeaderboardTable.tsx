import React from 'react';
import { ChevronRight, Sparkles } from 'lucide-react';
import { LeaderboardItem } from '../../types';
import { StatusBadge, StreakBadge, RankBadge, RankMovementBadge } from '../ui/Badge';

interface LeaderboardTableProps {
  items: LeaderboardItem[];
  isLoading: boolean;
  onSelectCreative: (id: string) => void;
}

export const LeaderboardTable: React.FC<LeaderboardTableProps> = ({
  items,
  isLoading,
  onSelectCreative,
}) => {
  if (isLoading) {
    return (
      <div className="w-full bg-[#0f172a]/90 border border-slate-800 rounded-2xl p-12 flex flex-col items-center justify-center gap-3">
        <div className="w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm font-semibold text-slate-400 font-mono">
          Loading Leaderboard Rankings...
        </span>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="w-full bg-[#0f172a]/90 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
        <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <h4 className="text-base font-bold text-slate-200">No Creatives Matched Filters</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
          Try clearing your status filters, lowering the minimum spend threshold, or running a fresh Meta sync.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full bg-[#0f172a]/95 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800/90 bg-[#111827]/80 text-[11px] font-extrabold uppercase tracking-wider text-slate-400 font-mono">
              <th className="py-3.5 pl-4 pr-2 text-center w-14">Rank</th>
              <th className="py-3.5 px-2 text-center w-12">Move</th>
              <th className="py-3.5 px-3 w-14">Preview</th>
              <th className="py-3.5 px-3">Creative Name & Client</th>
              <th className="py-3.5 px-3 text-right">Spend</th>
              <th className="py-3.5 px-3 text-right">ROAS</th>
              <th className="py-3.5 px-3 text-right">CTR</th>
              <th className="py-3.5 px-3 text-right">CPA</th>
              <th className="py-3.5 px-3 text-center">Days</th>
              <th className="py-3.5 px-3 text-center">Status</th>
              <th className="py-3.5 px-3 text-center">Streak</th>
              <th className="py-3.5 pr-4 pl-2 text-right w-12"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 text-sm">
            {items.map((item) => {
              const isWinner = item.status === 'WIN';
              const isLoser = item.status === 'LOSS';
              const rowHighlight =
                item.rank === 1
                  ? 'bg-amber-500/[0.04] hover:bg-amber-500/[0.08]'
                  : item.rank === 2
                  ? 'bg-slate-400/[0.03] hover:bg-slate-400/[0.06]'
                  : item.rank === 3
                  ? 'bg-amber-700/[0.03] hover:bg-amber-700/[0.06]'
                  : 'hover:bg-slate-800/40';

              return (
                <tr
                  key={item.id}
                  onClick={() => onSelectCreative(item.id)}
                  className={`transition-colors cursor-pointer group ${rowHighlight}`}
                >
                  {/* Rank Badge */}
                  <td className="py-3 pl-4 pr-2 text-center">
                    <RankBadge rank={item.rank} />
                  </td>

                  {/* 24h Rank Movement */}
                  <td className="py-3 px-2 text-center">
                    <RankMovementBadge
                      movement={item.rank_movement}
                      deltaVal={item.rank_movement_val}
                    />
                  </td>

                  {/* Thumbnail Image with hover preview */}
                  <td className="py-3 px-3">
                    <div className="w-11 h-11 rounded-lg overflow-hidden bg-slate-950 border border-slate-700/60 relative group/thumb">
                      <img
                        src={item.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&q=80'}
                        alt={item.name}
                        className="w-full h-full object-cover group-hover/thumb:scale-125 transition-transform duration-200"
                      />
                    </div>
                  </td>

                  {/* Creative Name & Client */}
                  <td className="py-3 px-3 max-w-xs">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold text-amber-400/90 uppercase font-mono px-1.5 py-0.2 rounded bg-amber-400/10 border border-amber-400/20">
                          {item.client_name}
                        </span>
                        {item.tags.length > 0 && (
                          <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.2 rounded">
                            {item.tags[0]}
                          </span>
                        )}
                      </div>
                      <span className="font-bold text-slate-100 truncate group-hover:text-amber-400 transition-colors mt-0.5">
                        {item.name}
                      </span>
                      {item.headline && (
                        <span className="text-[11px] text-slate-400 truncate">
                          "{item.headline}"
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Spend */}
                  <td className="py-3 px-3 text-right font-mono font-bold text-slate-200">
                    ${item.spend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>

                  {/* ROAS */}
                  <td className="py-3 px-3 text-right">
                    <div className="flex flex-col items-end">
                      <span
                        className={`text-base font-extrabold font-mono ${
                          isWinner
                            ? 'text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                            : isLoser
                            ? 'text-rose-400'
                            : 'text-cyan-400'
                        }`}
                      >
                        {item.roas.toFixed(2)}x
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        Target: {item.target_roas.toFixed(1)}x
                      </span>
                    </div>
                  </td>

                  {/* CTR */}
                  <td className="py-3 px-3 text-right font-mono font-semibold text-slate-300">
                    {item.ctr.toFixed(2)}%
                  </td>

                  {/* CPA */}
                  <td className="py-3 px-3 text-right font-mono font-semibold text-slate-300">
                    {item.cpa > 0 ? `$${item.cpa.toFixed(2)}` : '-'}
                  </td>

                  {/* Days Live */}
                  <td className="py-3 px-3 text-center font-mono text-xs font-semibold text-slate-400">
                    {item.days_live}d
                  </td>

                  {/* Status Pill */}
                  <td className="py-3 px-3 text-center">
                    <StatusBadge status={item.status} />
                  </td>

                  {/* Streak Flame / Ice */}
                  <td className="py-3 px-3 text-center">
                    <StreakBadge streak={item.streak} />
                  </td>

                  {/* View Details Action */}
                  <td className="py-3 pr-4 pl-2 text-right">
                    <div className="w-7 h-7 rounded-lg bg-slate-800/60 group-hover:bg-amber-400 group-hover:text-slate-950 flex items-center justify-center transition-colors">
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-950" />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
