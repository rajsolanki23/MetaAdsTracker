import React from 'react';
import { Edit3, Tag, MessageSquare, ArrowLeft } from 'lucide-react';
import { Creative, DailySnapshot } from '../../types';
import { StatusBadge, StreakBadge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface CreativeHeaderProps {
  creative: Creative;
  latestSnapshot?: DailySnapshot;
  targetRoas?: number;
  onBack: () => void;
  onEdit: () => void;
}

export const CreativeHeader: React.FC<CreativeHeaderProps> = ({
  creative,
  latestSnapshot,
  targetRoas = 2.5,
  onBack,
  onEdit,
}) => {
  return (
    <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl p-6 mb-6 backdrop-blur-md shadow-xl">
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-400 hover:text-amber-400 transition-colors mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Leaderboard</span>
      </button>

      <div className="flex flex-col lg:flex-row gap-6 items-start justify-between">
        {/* Left: Thumbnail & Main Details */}
        <div className="flex gap-5 items-start">
          <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-xl overflow-hidden bg-slate-950 border border-slate-700/80 shrink-0 shadow-lg relative group">
            <img
              src={creative.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=300&q=80'}
              alt={creative.name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            />
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              {latestSnapshot && <StatusBadge status={latestSnapshot.status} />}
              {latestSnapshot && <StreakBadge streak={latestSnapshot.streak} />}
              {creative.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 text-[10px] font-semibold text-slate-300 bg-slate-800/90 border border-slate-700 px-2 py-0.5 rounded-md"
                >
                  <Tag className="w-2.5 h-2.5 text-slate-400" />
                  {tag}
                </span>
              ))}
            </div>

            <h1 className="text-xl sm:text-2xl font-extrabold text-white">
              {creative.name}
            </h1>

            {creative.headline && (
              <p className="text-sm font-semibold text-amber-400 mt-1">
                "{creative.headline}"
              </p>
            )}

            {creative.body_copy && (
              <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 max-w-xl">
                {creative.body_copy}
              </p>
            )}

            {creative.notes && (
              <div className="flex items-center gap-1.5 text-xs text-slate-400 italic mt-2 bg-slate-900/60 px-2.5 py-1 rounded-md border border-slate-800 inline-flex">
                <MessageSquare className="w-3 h-3 text-slate-500" />
                <span>Notes: {creative.notes}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Quick Performance Stat Highlights */}
        {latestSnapshot && (
          <div className="flex flex-col items-end gap-3 w-full lg:w-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={onEdit}
              className="text-xs self-end"
            >
              <Edit3 className="w-3.5 h-3.5 mr-1" />
              <span>Edit / Override</span>
            </Button>

            <div className="grid grid-cols-3 gap-3 bg-slate-900/90 border border-slate-800 p-3 rounded-xl w-full sm:w-auto">
              <div className="text-center px-2">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block font-mono">
                  Today ROAS
                </span>
                <span className="text-lg font-extrabold font-mono text-emerald-400">
                  {latestSnapshot.roas.toFixed(2)}x
                </span>
                <span className="text-[10px] text-slate-500 block font-mono">
                  Target {targetRoas.toFixed(1)}x
                </span>
              </div>
              <div className="text-center px-2 border-x border-slate-800">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block font-mono">
                  Today Spend
                </span>
                <span className="text-base font-bold font-mono text-slate-100">
                  ${latestSnapshot.spend.toLocaleString()}
                </span>
                <span className="text-[10px] text-slate-500 block font-mono">
                  Rev ${latestSnapshot.revenue.toLocaleString()}
                </span>
              </div>
              <div className="text-center px-2">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block font-mono">
                  Today CPA
                </span>
                <span className="text-base font-bold font-mono text-slate-100">
                  ${latestSnapshot.cpa.toFixed(2)}
                </span>
                <span className="text-[10px] text-slate-500 block font-mono">
                  CTR {latestSnapshot.ctr.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
