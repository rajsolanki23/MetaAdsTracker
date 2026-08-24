import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { TrendPoint } from '../../types';
import { TrendingUp } from 'lucide-react';

interface CreativeTrendChartProps {
  data: TrendPoint[];
  targetRoas: number;
  isLoading: boolean;
}

export const CreativeTrendChart: React.FC<CreativeTrendChartProps> = ({
  data,
  targetRoas,
  isLoading,
}) => {
  const [metric, setMetric] = useState<'roas' | 'spend' | 'cpa'>('roas');

  if (isLoading) {
    return (
      <div className="h-80 bg-[#0f172a]/90 border border-slate-800 rounded-2xl p-6 flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-80 bg-[#0f172a]/90 border border-slate-800 rounded-2xl p-6 flex items-center justify-center text-slate-500 text-xs font-mono">
        No snapshot trend data available for this creative.
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload as TrendPoint;
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-xl shadow-2xl text-xs space-y-1 font-mono">
          <div className="font-bold text-slate-200 border-b border-slate-800 pb-1 mb-1">
            {point.date} ({point.status})
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">ROAS:</span>
            <span className="font-bold text-emerald-400">{point.roas.toFixed(2)}x</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Spend:</span>
            <span className="font-bold text-slate-200">${point.spend.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Revenue:</span>
            <span className="font-bold text-slate-200">${point.revenue.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">CPA:</span>
            <span className="font-bold text-slate-200">${point.cpa.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Streak:</span>
            <span className="font-bold text-amber-400">{point.streak > 0 ? `🔥 +${point.streak}d` : point.streak < 0 ? `❄️ ${point.streak}d` : '0d'}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl p-5 mb-6 backdrop-blur-md shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            30-Day Performance Trendline
          </h3>
        </div>

        {/* Metric Switcher */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setMetric('roas')}
            className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition-colors ${
              metric === 'roas'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ROAS
          </button>
          <button
            onClick={() => setMetric('spend')}
            className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition-colors ${
              metric === 'spend'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Spend ($)
          </button>
          <button
            onClick={() => setMetric('cpa')}
            className={`px-2.5 py-1 rounded text-xs font-mono font-bold transition-colors ${
              metric === 'cpa'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            CPA ($)
          </button>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="roasGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="spendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />

            <XAxis
              dataKey="date"
              stroke="#64748b"
              fontSize={10}
              tickFormatter={(val) => val.split('-').slice(1).join('/')}
            />
            <YAxis stroke="#64748b" fontSize={10} />

            <Tooltip content={<CustomTooltip />} />

            {metric === 'roas' && (
              <ReferenceLine
                y={targetRoas}
                stroke="#f59e0b"
                strokeDasharray="4 4"
                strokeWidth={2}
                label={{
                  value: `Target ROAS: ${targetRoas.toFixed(1)}x`,
                  fill: '#f59e0b',
                  fontSize: 10,
                  position: 'insideTopRight',
                }}
              />
            )}

            {metric === 'roas' && (
              <Area
                type="monotone"
                dataKey="roas"
                stroke="#10b981"
                strokeWidth={2.5}
                fill="url(#roasGradient)"
                dot={{ r: 3, fill: '#10b981' }}
                activeDot={{ r: 6, fill: '#34d399' }}
              />
            )}

            {metric === 'spend' && (
              <Area
                type="monotone"
                dataKey="spend"
                stroke="#06b6d4"
                strokeWidth={2.5}
                fill="url(#spendGradient)"
                dot={{ r: 3, fill: '#06b6d4' }}
              />
            )}

            {metric === 'cpa' && (
              <Line
                type="monotone"
                dataKey="cpa"
                stroke="#f59e0b"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#f59e0b' }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
