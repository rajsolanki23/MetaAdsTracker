import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Trophy, AlertTriangle, CheckCircle2, DollarSign, Target, RefreshCw } from 'lucide-react';
import { Client } from '../../types';
import { Button } from '../ui/Button';

interface ClientCardsGridProps {
  clients: Client[];
  isLoading: boolean;
  onEditClient: (client: Client) => void;
  onSyncClient: (clientId: string) => void;
}

export const ClientCardsGrid: React.FC<ClientCardsGridProps> = ({
  clients,
  isLoading,
  onEditClient,
  onSyncClient,
}) => {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((n) => (
          <div key={n} className="h-64 rounded-2xl bg-slate-900/60 border border-slate-800 animate-pulse" />
        ))}
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl">
        <h4 className="text-base font-bold text-slate-200">No Client Accounts Found</h4>
        <p className="text-xs text-slate-500 mt-1">
          Click "Add New Client" to connect your first Meta ad account.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {clients.map((client) => {
        const isHealthy = client.health_status === 'HEALTHY';
        const isWarning = client.health_status === 'WARNING';

        return (
          <div
            key={client._id}
            className="rounded-2xl bg-[#0f172a]/95 border border-slate-800 hover:border-slate-700 shadow-xl p-5 backdrop-blur-md flex flex-col justify-between transition-all duration-200 hover:-translate-y-1 group"
          >
            {/* Header */}
            <div>
              <div className="flex items-start justify-between gap-3 mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white group-hover:text-amber-400 transition-colors">
                    {client.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
                      {client.currency} • {client.timezone.split('/')[1] || client.timezone}
                    </span>
                    {client.meta_account_id && (
                      <span className="text-[10px] font-mono text-emerald-400">
                        {client.meta_account_id}
                      </span>
                    )}
                  </div>
                </div>

                {/* Health Badge */}
                <span
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-extrabold uppercase border ${
                    isHealthy
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : isWarning
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}
                >
                  {isHealthy ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                  {client.health_status}
                </span>
              </div>

              {/* Blended Metrics Card */}
              <div className="grid grid-cols-2 gap-3 bg-slate-900/90 rounded-xl p-3.5 border border-slate-800 mb-4">
                <div>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400 font-semibold mb-0.5">
                    <Target className="w-3.5 h-3.5 text-amber-400" />
                    <span>Blended ROAS</span>
                  </div>
                  <div className="text-xl font-extrabold font-mono text-emerald-400">
                    {client.blended_roas.toFixed(2)}x
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                    Target: {client.target_roas.toFixed(1)}x
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400 font-semibold mb-0.5">
                    <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                    <span>Total Spend</span>
                  </div>
                  <div className="text-xl font-extrabold font-mono text-slate-100">
                    ${client.blended_spend.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                    Rev: ${client.blended_revenue.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Status Breakdown Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-[11px] font-semibold text-slate-400 mb-1.5 font-mono">
                  <span>CREATIVES ({client.active_creatives_count})</span>
                  <span className="text-emerald-400 font-bold">{client.wins_count} WINS</span>
                </div>
                <div className="flex h-2 rounded-full overflow-hidden bg-slate-800 gap-0.5">
                  {client.wins_count > 0 && (
                    <div
                      style={{ width: `${(client.wins_count / (client.active_creatives_count || 1)) * 100}%` }}
                      className="bg-emerald-500"
                      title={`${client.wins_count} Wins`}
                    />
                  )}
                  {client.testing_count > 0 && (
                    <div
                      style={{ width: `${(client.testing_count / (client.active_creatives_count || 1)) * 100}%` }}
                      className="bg-cyan-500"
                      title={`${client.testing_count} Testing`}
                    />
                  )}
                  {client.losses_count > 0 && (
                    <div
                      style={{ width: `${(client.losses_count / (client.active_creatives_count || 1)) * 100}%` }}
                      className="bg-rose-500"
                      title={`${client.losses_count} Losses`}
                    />
                  )}
                </div>
              </div>

              {/* Best Creative Highlight */}
              {client.best_creative_name && (
                <div className="text-xs bg-emerald-950/30 border border-emerald-500/20 rounded-lg p-2.5 mb-4">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[10px] uppercase font-mono">
                    <Trophy className="w-3.5 h-3.5" />
                    <span>Best Creative ({client.best_creative_roas?.toFixed(2)}x ROAS)</span>
                  </div>
                  <div className="text-slate-200 font-medium truncate mt-0.5">
                    {client.best_creative_name}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onSyncClient(client._id)}
                className="text-xs"
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Sync
              </Button>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onEditClient(client)}
                  className="text-xs"
                >
                  Edit
                </Button>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate(`/?client_id=${client._id}`)}
                  className="text-xs"
                >
                  <span>Leaderboard</span>
                  <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
