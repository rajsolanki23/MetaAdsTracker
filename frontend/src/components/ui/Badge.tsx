import React from 'react';
import { Flame, Snowflake, ArrowUp, ArrowDown, Minus, Sparkles, Trophy, Award, Medal } from 'lucide-react';
import { StatusType } from '../../types';

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const configs = {
    WIN: {
      label: 'WIN',
      style: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]',
      dot: 'bg-emerald-400',
    },
    LOSS: {
      label: 'LOSS',
      style: 'bg-rose-500/15 text-rose-400 border-rose-500/30 shadow-[0_0_10px_rgba(244,63,94,0.2)]',
      dot: 'bg-rose-400',
    },
    TESTING: {
      label: 'TESTING',
      style: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.2)]',
      dot: 'bg-cyan-400 animate-pulse',
    },
    PAUSED: {
      label: 'PAUSED',
      style: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
      dot: 'bg-slate-400',
    },
  };

  const config = configs[status] || configs.PAUSED;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase border ${config.style} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
};

interface StreakBadgeProps {
  streak: number;
  className?: string;
}

export const StreakBadge: React.FC<StreakBadgeProps> = ({ streak, className = '' }) => {
  if (streak === 0) {
    return <span className="text-xs text-slate-500 font-mono">-</span>;
  }

  if (streak > 0) {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-orange-500/15 text-orange-400 border border-orange-500/30 text-xs font-mono font-bold shadow-[0_0_10px_rgba(249,115,22,0.25)] ${className}`}
        title={`${streak} consecutive winning days`}
      >
        <Flame className="w-3.5 h-3.5 text-orange-400 animate-pulse-flame fill-orange-400" />
        <span>{streak}d</span>
      </span>
    );
  }

  const absStreak = Math.abs(streak);
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-sky-500/15 text-sky-400 border border-sky-500/30 text-xs font-mono font-bold shadow-[0_0_10px_rgba(56,189,248,0.2)] ${className}`}
      title={`${absStreak} consecutive losing days`}
    >
      <Snowflake className="w-3.5 h-3.5 text-sky-400" />
      <span>{absStreak}d</span>
    </span>
  );
};

interface RankBadgeProps {
  rank: number;
  className?: string;
}

export const RankBadge: React.FC<RankBadgeProps> = ({ rank, className = '' }) => {
  if (rank === 1) {
    return (
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center font-extrabold text-xs rank-badge-1 ${className}`}
        title="Rank #1 Gold Champion"
      >
        <Trophy className="w-4 h-4" />
      </div>
    );
  }
  if (rank === 2) {
    return (
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center font-extrabold text-xs rank-badge-2 ${className}`}
        title="Rank #2 Silver"
      >
        <Medal className="w-4 h-4" />
      </div>
    );
  }
  if (rank === 3) {
    return (
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center font-extrabold text-xs rank-badge-3 ${className}`}
        title="Rank #3 Bronze"
      >
        <Award className="w-4 h-4" />
      </div>
    );
  }

  return (
    <div
      className={`w-7 h-7 rounded-lg flex items-center justify-center font-mono font-bold text-xs bg-slate-800/80 text-slate-300 border border-slate-700/60 ${className}`}
    >
      #{rank}
    </div>
  );
};

interface RankMovementBadgeProps {
  movement: string;
  deltaVal: number;
  className?: string;
}

export const RankMovementBadge: React.FC<RankMovementBadgeProps> = ({ movement, deltaVal, className = '' }) => {
  if (movement === 'NEW') {
    return (
      <span
        className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30 ${className}`}
        title="New Creative Added Today"
      >
        <Sparkles className="w-2.5 h-2.5" />
        NEW
      </span>
    );
  }

  if (deltaVal > 0) {
    return (
      <span
        className={`inline-flex items-center gap-0.5 text-xs font-mono font-bold text-emerald-400 ${className}`}
        title={`Climbed ${deltaVal} ranks vs yesterday`}
      >
        <ArrowUp className="w-3.5 h-3.5 text-emerald-400 stroke-[3]" />
        +{deltaVal}
      </span>
    );
  }

  if (deltaVal < 0) {
    return (
      <span
        className={`inline-flex items-center gap-0.5 text-xs font-mono font-bold text-rose-400 ${className}`}
        title={`Dropped ${Math.abs(deltaVal)} ranks vs yesterday`}
      >
        <ArrowDown className="w-3.5 h-3.5 text-rose-400 stroke-[3]" />
        {deltaVal}
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center text-xs font-mono text-slate-500 ${className}`} title="Rank unchanged">
      <Minus className="w-3.5 h-3.5" />
    </span>
  );
};
