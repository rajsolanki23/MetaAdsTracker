import React from 'react';
import { SyncLog } from '../../types';
import { CheckCircle2, AlertCircle, Shield } from 'lucide-react';

interface SyncAuditLogsTableProps {
  logs: SyncLog[];
  isLoading: boolean;
}

export const SyncAuditLogsTable: React.FC<SyncAuditLogsTableProps> = ({
  logs,
  isLoading,
}) => {
  if (isLoading) {
    return <div className="p-6 text-center text-xs text-slate-400 font-mono">Loading sync audit logs...</div>;
  }

  if (logs.length === 0) {
    return <div className="p-6 text-center text-xs text-slate-500 font-mono">No sync logs recorded yet.</div>;
  }

  return (
    <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl overflow-hidden shadow-xl backdrop-blur-md">
      <div className="px-5 py-3.5 border-b border-slate-800 bg-[#111827]/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Meta API Sync Audit Logs
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Last {logs.length} Operations
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] uppercase text-slate-400 bg-slate-900/40">
              <th className="py-2.5 px-4">Timestamp</th>
              <th className="py-2.5 px-3">Client Account</th>
              <th className="py-2.5 px-3">Sync Type</th>
              <th className="py-2.5 px-3 text-center">Status</th>
              <th className="py-2.5 px-3 text-right">Records Synced</th>
              <th className="py-2.5 px-3 text-right">Duration</th>
              <th className="py-2.5 px-4">Diagnostics / Error</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40">
            {logs.map((log) => (
              <tr key={log._id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 px-4 text-slate-400">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-2.5 px-3 font-bold text-slate-200">
                  {log.client_name || 'All Clients'}
                </td>
                <td className="py-2.5 px-3">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                    {log.sync_type}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-center">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      log.status === 'SUCCESS'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                    }`}
                  >
                    {log.status === 'SUCCESS' ? (
                      <CheckCircle2 className="w-3 h-3" />
                    ) : (
                      <AlertCircle className="w-3 h-3" />
                    )}
                    {log.status}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-right text-slate-200 font-bold">
                  {log.records_synced}
                </td>
                <td className="py-2.5 px-3 text-right text-slate-400">
                  {log.duration_ms}ms
                </td>
                <td className="py-2.5 px-4 text-slate-400 truncate max-w-xs">
                  {log.error_message ? (
                    <span className="text-rose-400 font-semibold">{log.error_message}</span>
                  ) : (
                    <span className="text-slate-500">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
