import React from 'react';
import { Search, ArrowUpDown, Filter, X } from 'lucide-react';
import { Client, StatusType } from '../../types';
import { Slider } from '../ui/Slider';

interface LeaderboardFiltersProps {
  clients: Client[];
  selectedClientId: string;
  onSelectClient: (clientId: string) => void;
  selectedStatuses: StatusType[];
  onToggleStatus: (status: StatusType) => void;
  minSpend: number;
  onChangeMinSpend: (val: number) => void;
  search: string;
  onChangeSearch: (val: string) => void;
  sortBy: string;
  onChangeSortBy: (sort: string) => void;
  sortDir: string;
  onToggleSortDir: () => void;
  onResetFilters: () => void;
}

export const LeaderboardFilters: React.FC<LeaderboardFiltersProps> = ({
  selectedClientId,
  selectedStatuses,
  onToggleStatus,
  minSpend,
  onChangeMinSpend,
  search,
  onChangeSearch,
  sortBy,
  onChangeSortBy,
  sortDir,
  onToggleSortDir,
  onResetFilters,
}) => {
  const statusOptions: { label: string; value: StatusType; color: string }[] = [
    { label: 'WIN', value: 'WIN', color: 'border-emerald-500/50 text-emerald-400 bg-emerald-500/10' },
    { label: 'LOSS', value: 'LOSS', color: 'border-rose-500/50 text-rose-400 bg-rose-500/10' },
    { label: 'TESTING', value: 'TESTING', color: 'border-cyan-500/50 text-cyan-400 bg-cyan-500/10' },
    { label: 'PAUSED', value: 'PAUSED', color: 'border-slate-500/50 text-slate-400 bg-slate-500/10' },
  ];

  const sortOptions = [
    { label: 'ROAS', value: 'roas' },
    { label: 'Spend', value: 'spend' },
    { label: 'CTR (%)', value: 'ctr' },
    { label: 'CPA ($)', value: 'cpa' },
    { label: 'Streak', value: 'streak' },
    { label: 'Days Live', value: 'days_live' },
  ];

  const hasActiveFilters =
    Boolean(selectedClientId) ||
    selectedStatuses.length > 0 ||
    minSpend > 0 ||
    Boolean(search);

  return (
    <div className="bg-[#0f172a]/90 border border-slate-800 rounded-2xl p-4 mb-6 backdrop-blur-md shadow-xl">
      <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
        {/* Search Bar */}
        <div className="relative w-full lg:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search creatives, tags, copy..."
            value={search}
            onChange={(e) => onChangeSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900/90 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-400 transition-colors"
          />
          {search && (
            <button
              onClick={() => onChangeSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Status Multi-Select Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-bold text-slate-400 uppercase mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Status:
          </span>
          {statusOptions.map((opt) => {
            const isSelected = selectedStatuses.includes(opt.value);
            return (
              <button
                key={opt.value}
                onClick={() => onToggleStatus(opt.value)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold tracking-wider uppercase border transition-all ${
                  isSelected
                    ? `${opt.color} shadow-sm ring-1 ring-white/10 scale-105`
                    : 'border-slate-800 bg-slate-900/60 text-slate-500 hover:text-slate-300 hover:border-slate-700'
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2 w-full lg:w-auto justify-end">
          <span className="text-[11px] font-bold text-slate-400 uppercase hidden sm:inline">
            Sort:
          </span>
          <select
            value={sortBy}
            onChange={(e) => onChangeSortBy(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-xs font-semibold text-slate-200 focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <button
            onClick={onToggleSortDir}
            className="p-1.5 bg-slate-900 border border-slate-700/80 hover:border-slate-600 rounded-lg text-slate-300 hover:text-amber-400 transition-colors"
            title={`Sort Direction: ${sortDir.toUpperCase()}`}
          >
            <ArrowUpDown className="w-4 h-4" />
          </button>

          {hasActiveFilters && (
            <button
              onClick={onResetFilters}
              className="text-xs font-semibold text-rose-400 hover:text-rose-300 ml-2 underline underline-offset-4"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Secondary Controls Bar: Min Spend Slider */}
      <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="w-full sm:w-80">
          <Slider
            label="Min Spend Threshold"
            min={0}
            max={600}
            step={25}
            value={minSpend}
            onChange={onChangeMinSpend}
          />
        </div>
        <div className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
          <span>Target Metric:</span>
          <span className="text-amber-400 font-bold uppercase">{sortBy} ({sortDir})</span>
        </div>
      </div>
    </div>
  );
};
