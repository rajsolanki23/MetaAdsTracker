import React, { useState, useEffect } from 'react';
import { Client } from '../../types';
import { Dialog } from '../ui/Dialog';
import { Input, Select } from '../ui/Input';
import { Button } from '../ui/Button';
import { useCreateClient, useUpdateClient, useDeleteClient, useTestMetaConnection } from '../../api/queries';
import { useToast } from '../ui/Toast';
import { CheckCircle2, AlertCircle } from 'lucide-react';

interface ClientFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  client?: Client | null;
}

export const ClientFormModal: React.FC<ClientFormModalProps> = ({
  isOpen,
  onClose,
  client,
}) => {
  const [name, setName] = useState('');
  const [metaAccountId, setMetaAccountId] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [targetRoas, setTargetRoas] = useState('2.5');
  const [minSpendThreshold, setMinSpendThreshold] = useState('100.0');
  const [currency, setCurrency] = useState('USD');
  const [timezone, setTimezone] = useState('America/New_York');

  const [testResult, setTestResult] = useState<{ valid: boolean; message: string } | null>(null);

  const createClient = useCreateClient();
  const updateClient = useUpdateClient();
  const deleteClient = useDeleteClient();
  const testConnection = useTestMetaConnection();
  const { showToast } = useToast();

  useEffect(() => {
    if (client) {
      setName(client.name);
      setMetaAccountId(client.meta_account_id || '');
      setAccessToken(client.access_token || '');
      setTargetRoas(client.target_roas.toString());
      setMinSpendThreshold(client.min_spend_threshold.toString());
      setCurrency(client.currency);
      setTimezone(client.timezone);
      setTestResult(null);
    } else {
      setName('');
      setMetaAccountId('');
      setAccessToken('');
      setTargetRoas('2.5');
      setMinSpendThreshold('100.0');
      setCurrency('USD');
      setTimezone('America/New_York');
      setTestResult(null);
    }
  }, [client, isOpen]);

  const handleTestToken = async () => {
    if (!metaAccountId || !accessToken) {
      showToast('Please enter both Ad Account ID and Access Token to test', 'error');
      return;
    }
    try {
      const res = await testConnection.mutateAsync({
        meta_account_id: metaAccountId,
        access_token: accessToken,
      });
      setTestResult({
        valid: true,
        message: `Connected successfully to "${res.account_name}" (${res.account_id})!`,
      });
      showToast('Meta token verified!', 'success');
    } catch (err: any) {
      setTestResult({
        valid: false,
        message: err.message || 'Connection failed. Please verify credentials.',
      });
      showToast(err.message || 'Token verification failed', 'error');
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      showToast('Client name is required', 'error');
      return;
    }

    const payload = {
      name: name.trim(),
      meta_account_id: metaAccountId.trim() || undefined,
      access_token: accessToken.trim() || undefined,
      target_roas: parseFloat(targetRoas) || 2.5,
      min_spend_threshold: parseFloat(minSpendThreshold) || 100.0,
      currency,
      timezone,
      is_active: true,
    };

    try {
      if (client) {
        await updateClient.mutateAsync({ id: client._id, data: payload });
        showToast(`Client "${name}" updated successfully!`, 'success');
      } else {
        await createClient.mutateAsync(payload);
        showToast(`Client "${name}" created successfully!`, 'success');
      }
      onClose();
    } catch (err: any) {
      showToast(err.message || 'Failed to save client', 'error');
    }
  };

  const handleDelete = async () => {
    if (!client) return;
    if (confirm(`Are you sure you want to remove client "${client.name}"?`)) {
      try {
        await deleteClient.mutateAsync(client._id);
        showToast(`Client "${client.name}" removed`, 'info');
        onClose();
      } catch (err: any) {
        showToast(err.message || 'Failed to delete client', 'error');
      }
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={client ? 'Edit Client Settings' : 'Add New Client Account'}
      description="Configure target ROAS, evaluation thresholds, and Meta API credentials."
      maxWidth="lg"
    >
      <form onSubmit={handleSave} className="space-y-4">
        <Input
          label="Client / Brand Name"
          placeholder="e.g. Aura Skincare"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Target ROAS (Threshold for WIN)"
            type="number"
            step="0.1"
            min="0"
            placeholder="2.5"
            value={targetRoas}
            onChange={(e) => setTargetRoas(e.target.value)}
            helperText="ROAS >= target classified as WIN"
            required
          />

          <Input
            label="Min Spend Threshold ($)"
            type="number"
            step="10"
            min="0"
            placeholder="100.00"
            value={minSpendThreshold}
            onChange={(e) => setMinSpendThreshold(e.target.value)}
            helperText="Spend < min is classified as TESTING"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            options={[
              { value: 'USD', label: 'USD ($)' },
              { value: 'EUR', label: 'EUR (€)' },
              { value: 'GBP', label: 'GBP (£)' },
              { value: 'CAD', label: 'CAD ($)' },
              { value: 'AUD', label: 'AUD ($)' },
            ]}
          />

          <Select
            label="Timezone"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            options={[
              { value: 'America/New_York', label: 'Eastern Time (US)' },
              { value: 'America/Chicago', label: 'Central Time (US)' },
              { value: 'America/Denver', label: 'Mountain Time (US)' },
              { value: 'America/Los_Angeles', label: 'Pacific Time (US)' },
              { value: 'Europe/London', label: 'London (GMT/BST)' },
              { value: 'UTC', label: 'UTC Universal' },
            ]}
          />
        </div>

        {/* Meta Graph API Credentials */}
        <div className="pt-3 border-t border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400 font-mono">
              Meta Marketing API Integration
            </span>
            <button
              type="button"
              onClick={handleTestToken}
              disabled={testConnection.isPending}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 disabled:opacity-50"
            >
              {testConnection.isPending ? 'Verifying...' : '⚡ Test Connection'}
            </button>
          </div>

          <Input
            label="Meta Ad Account ID"
            placeholder="e.g. act_1234567890"
            value={metaAccountId}
            onChange={(e) => setMetaAccountId(e.target.value)}
            helperText="Found in Meta Ads Manager URL or Account Settings"
          />

          <Input
            label="Meta Access Token"
            type="password"
            placeholder="EAAB..."
            value={accessToken}
            onChange={(e) => setAccessToken(e.target.value)}
            helperText="User or System User Token with ads_read permission"
          />

          {testResult && (
            <div
              className={`p-3 rounded-xl text-xs flex items-start gap-2 ${
                testResult.valid
                  ? 'bg-emerald-950/60 border border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-950/60 border border-rose-500/30 text-rose-300'
              }`}
            >
              {testResult.valid ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
          {client ? (
            <Button
              type="button"
              variant="danger"
              size="sm"
              onClick={handleDelete}
              disabled={deleteClient.isPending}
            >
              Delete Client
            </Button>
          ) : (
            <div />
          )}

          <div className="flex items-center gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={createClient.isPending || updateClient.isPending}
            >
              Save Client
            </Button>
          </div>
        </div>
      </form>
    </Dialog>
  );
};
