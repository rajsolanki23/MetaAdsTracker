import React from 'react';
import { Trophy, Medal, Award, ArrowUp, ArrowDown } from 'lucide-react';
import { LeaderboardItem } from '../../types';
import { StatusBadge, StreakBadge } from '../ui/Badge';

interface PodiumTop3Props {
  items: LeaderboardItem[];
  onSelectCreative: (id: string) => void;
}

export const PodiumTop3: React.FC<PodiumTop3Props> = ({ items, onSelectCreative }) => {
  if (items.length === 0) return null;

  const first = items[0];
  const second = items[1];
  const third = items[2];

  const renderPodiumCard = (
    item: LeaderboardItem | undefined,
    place: 1 | 2 | 3,
    heightClass: string,
    glowClass: string,
    borderClass: string
  ) => {
    if (!item) {
      return (
        <div className={`flex-1 rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 flex items-center justify-center ${heightClass}`}>
          <span className="text-xs text-slate-600 font-mono">No Rank #{place}</span>
        </div>
      );
    }

    const icons = {
      1: <Trophy className="w-5 h-5 text-amber-400 fill-amber-400" />,
      2: <Medal className="w-5 h-5 text-slate-300 fill-slate-300" />,
      3: <Award className="w-5 h-5 text-amber-600 fill-amber-600" />,
    };

    const headers = {
      1: 'bg-gradient-to-r from-amber-500/20 via-amber-400/30 to-amber-500/20 text-amber-300 border-amber-500/40',
      2: 'bg-gradient-to-r from-slate-400/20 via-slate-300/30 to-slate-400/20 text-slate-200 border-slate-400/40',
      3: 'bg-gradient-to-r from-amber-700/20 via-amber-600/30 to-amber-700/20 text-amber-400 border-amber-600/40',
    };

    return (
      <div
        onClick={() => onSelectCreative(item.id)}
        className={`flex-1 rounded-2xl bg-[#0f172a]/95 border ${borderClass} ${glowClass} p-4 transition-all duration-300 hover:-translate-y-1 cursor-pointer flex flex-col justify-between relative overflow-hidden group`}
      >
        {/* Top Header Badge */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-mono font-extrabold ${headers[place]}`}>
            {icons[place]}
            <span>RANK #{place}</span>
          </div>
          <StatusBadge status={item.status} />
        </div>

        {/* Creative Info */}
        <div className="flex gap-3 items-center mb-3">
          <div className="w-14 h-14 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shrink-0 relative">
            <img
              src={item.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&q=80'}
              alt={item.name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            />
          </div>
          <div className="min-w-0 flex-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block truncate">
              {item.client_name}
            </span>
            <h4 className="text-sm font-bold text-slate-100 truncate group-hover:text-amber-400 transition-colors">
              {item.name}
            </h4>
            <div className="flex items-center gap-2 mt-1">
              <StreakBadge streak={item.streak} />
              {item.rank_movement_val !== 0 && (
                <span className={`text-[11px] font-mono font-bold flex items-center gap-0.5 ${item.rank_movement_val > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {item.rank_movement_val > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                  {item.rank_movement_val > 0 ? `+${item.rank_movement_val}` : item.rank_movement_val}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Metric Highlight Grid */}
        <div className="grid grid-cols-3 gap-2 bg-slate-900/80 rounded-xl p-2.5 border border-slate-800/80">
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">ROAS</span>
            <span className="text-base font-extrabold font-mono text-emerald-400">
              {item.roas.toFixed(2)}x
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">Spend</span>
            <span className="text-xs font-bold font-mono text-slate-200">
              ${item.spend.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-semibold">CPA</span>
            <span className="text-xs font-bold font-mono text-slate-200">
              ${item.cpa.toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-3">
        <Trophy className="w-4 h-4 text-amber-400" />
        <h3 className="text-xs font-extrabold uppercase tracking-widest text-slate-400 font-mono">
          TOP 3 PODIUM CHAMPIONS
        </h3>
      </div>
      <div className="flex flex-col md:flex-row gap-4 items-stretch">
        {renderPodiumCard(
          second,
          2,
          'min-h-[160px]',
          'shadow-[0_0_20px_rgba(226,232,240,0.1)]',
          'border-slate-700/80'
        )}
        {renderPodiumCard(
          first,
          1,
          'min-h-[180px] md:-translate-y-2',
          'shadow-[0_0_30px_rgba(245,158,11,0.25)] ring-1 ring-amber-400/40',
          'border-amber-500/50'
        )}
        {renderPodiumCard(
          third,
          3,
          'min-h-[160px]',
          'shadow-[0_0_20px_rgba(217,119,6,0.15)]',
          'border-amber-700/60'
        )}
      </div>
    </div>
  );
};
