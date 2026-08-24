import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Client } from '../../types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { useTriggerClientSync, useTestMetaConnection, useUpdateClient } from '../../api/queries';
import { useToast } from '../ui/Toast';
import { RefreshCw, Shield, Clock, Plus } from 'lucide-react';

interface MetaSyncSettingsProps {
  clients: Client[];
}

export const MetaSyncSettings: React.FC<MetaSyncSettingsProps> = ({ clients }) => {
  const navigate = useNavigate();
  const [selectedClientId, setSelectedClientId] = useState(clients[0]?._id || '');
  const selectedClient = clients.find((c) => c._id === selectedClientId) || clients[0];

  const [metaAccountId, setMetaAccountId] = useState(selectedClient?.meta_account_id || '');
  const [accessToken, setAccessToken] = useState(selectedClient?.access_token || '');

  React.useEffect(() => {
    if (selectedClient) {
      setMetaAccountId(selectedClient.meta_account_id || '');
      setAccessToken(selectedClient.access_token || '');
    }
  }, [selectedClient]);

  React.useEffect(() => {
    if (!selectedClientId && clients.length > 0) {
      setSelectedClientId(clients[0]._id);
    }
  }, [clients, selectedClientId]);

  const triggerSync = useTriggerClientSync();
  const testConnection = useTestMetaConnection();
  const updateClient = useUpdateClient();
  const { showToast } = useToast();

  const handleTest = async () => {
    if (!metaAccountId || !accessToken) {
      showToast('Please enter both Ad Account ID and Access Token', 'error');
      return;
    }
    try {
      const res = await testConnection.mutateAsync({
        meta_account_id: metaAccountId,
        access_token: accessToken,
      });
      showToast(`Token valid! Connected to ${res.account_name}`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Token test failed', 'error');
    }
  };

  const handleSaveCredentials = async () => {
    if (!selectedClient) return;
    try {
      await updateClient.mutateAsync({
        id: selectedClient._id,
        data: {
          meta_account_id: metaAccountId.trim(),
          access_token: accessToken.trim(),
        },
      });
      showToast('Meta credentials updated successfully!', 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to update credentials', 'error');
    }
  };

  const handleSyncNow = async () => {
    if (!selectedClient) return;
    try {
      showToast(`Syncing insights for ${selectedClient.name}...`, 'info');
      const res = await triggerSync.mutateAsync({ clientId: selectedClient._id });
      showToast(`Sync complete! ${res.records_synced} creatives updated.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Sync failed', 'error');
    }
  };

  if (clients.length === 0) {
    return (
      <div className="bg-[#0f172a]/95 border border-dashed border-slate-800 rounded-2xl p-8 text-center backdrop-blur-md">
        <Shield className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <h3 className="text-base font-bold text-slate-200">No Client Accounts Connected</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Add your first client account to connect Meta Ad Account IDs and automate 4-hour background syncs.
        </p>
        <Button
          variant="primary"
          size="sm"
          onClick={() => navigate('/clients')}
          className="mt-4 text-xs font-mono"
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          <span>Add Client Account</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Account Selector Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
        {clients.map((c) => (
          <button
            key={c._id}
            onClick={() => setSelectedClientId(c._id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold font-mono transition-all shrink-0 ${
              selectedClientId === c._id
                ? 'bg-amber-400 text-slate-950 shadow-[0_0_15px_rgba(245,158,11,0.3)]'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {selectedClient ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Credentials Card */}
          <div className="lg:col-span-2 bg-[#0f172a]/95 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white">
                  Meta Marketing API Credentials
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Connect {selectedClient.name}'s Meta ad account to automate 4-hour performance syncs.
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleTest}
                isLoading={testConnection.isPending}
                className="text-xs"
              >
                <Shield className="w-3.5 h-3.5 mr-1" />
                <span>Test Connection</span>
              </Button>
            </div>

            <div className="space-y-4">
              <Input
                label="Meta Ad Account ID"
                placeholder="act_123456789"
                value={metaAccountId}
                onChange={(e) => setMetaAccountId(e.target.value)}
                helperText="Format: act_XXXXXXXXX"
              />

              <Input
                label="Meta System User / User Access Token"
                type="password"
                placeholder="EAAB..."
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                helperText="Requires 'ads_read' and 'read_insights' permissions."
              />

              <div className="pt-2 flex items-center justify-between">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSaveCredentials}
                  isLoading={updateClient.isPending}
                >
                  Save Credentials
                </Button>
              </div>
            </div>
          </div>

          {/* Sync Status & Trigger Card */}
          <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                  Sync Status
                </h3>
              </div>

              <div className="space-y-3 bg-slate-900/80 rounded-xl p-4 border border-slate-800 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-400">Schedule:</span>
                  <span className="text-emerald-400 font-bold">Every 4 Hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Last Synced:</span>
                  <span className="text-slate-200">
                    {selectedClient.last_sync_at
                      ? new Date(selectedClient.last_sync_at).toLocaleTimeString()
                      : 'Never'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Status:</span>
                  <span
                    className={`font-bold ${
                      selectedClient.last_sync_status === 'SUCCESS'
                        ? 'text-emerald-400'
                        : selectedClient.last_sync_status === 'FAILED'
                        ? 'text-rose-400'
                        : 'text-slate-400'
                    }`}
                  >
                    {selectedClient.last_sync_status || 'PENDING'}
                  </span>
                </div>
                {selectedClient.last_sync_error && (
                  <div className="text-rose-400 text-[11px] pt-1 border-t border-slate-800">
                    Error: {selectedClient.last_sync_error}
                  </div>
                )}
              </div>
            </div>

            <div className="pt-6">
              <Button
                variant="primary"
                size="md"
                onClick={handleSyncNow}
                isLoading={triggerSync.isPending}
                className="w-full font-mono text-xs uppercase"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                <span>Trigger Manual Sync Now</span>
              </Button>
              <p className="text-[10px] text-slate-500 text-center mt-2 font-mono">
                Stores immutable daily snapshot for today
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
