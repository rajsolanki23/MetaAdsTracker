import React from 'react';
import { useClients, useSyncLogs } from '../api/queries';
import { MetaSyncSettings } from '../components/meta-sync/MetaSyncSettings';
import { SyncAuditLogsTable } from '../components/meta-sync/SyncAuditLogsTable';
import { RefreshCw } from 'lucide-react';

export const MetaSyncPage: React.FC = () => {
  const { data: clients = [] } = useClients();
  const { data: logs = [], isLoading: isLoadingLogs } = useSyncLogs(50);

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <RefreshCw className="w-5 h-5 text-amber-400" />
          <h1 className="text-xl font-extrabold text-white">Meta Marketing API Sync Settings</h1>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Manage live credentials, verify access tokens, trigger manual syncs, and monitor audit logs.
        </p>
      </div>

      {/* Connection & Trigger Controls */}
      <MetaSyncSettings clients={clients} />

      {/* Sync Execution Audit Logs Table */}
      <SyncAuditLogsTable logs={logs} isLoading={isLoadingLogs} />
    </div>
  );
};
