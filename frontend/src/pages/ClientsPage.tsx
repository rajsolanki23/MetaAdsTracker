import React, { useState } from 'react';
import { useClients, useTriggerClientSync } from '../api/queries';
import { Client } from '../types';
import { ClientCardsGrid } from '../components/clients/ClientCardsGrid';
import { ClientFormModal } from '../components/clients/ClientFormModal';
import { Button } from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';
import { Plus, LayoutGrid } from 'lucide-react';

export const ClientsPage: React.FC = () => {
  const { data: clients = [], isLoading } = useClients();
  const [selectedClientForEdit, setSelectedClientForEdit] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const triggerSync = useTriggerClientSync();
  const { showToast } = useToast();

  const handleOpenAdd = () => {
    setSelectedClientForEdit(null);
    setIsModalOpen(true);
  };

  const handleEditClient = (client: Client) => {
    setSelectedClientForEdit(client);
    setIsModalOpen(true);
  };

  const handleSyncClient = async (clientId: string) => {
    const client = clients.find((c) => c._id === clientId);
    try {
      showToast(`Triggering Meta sync for ${client?.name || 'client'}...`, 'info');
      const res = await triggerSync.mutateAsync({ clientId });
      showToast(`Sync complete! ${res.records_synced} creatives updated.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Sync failed', 'error');
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <LayoutGrid className="w-5 h-5 text-amber-400" />
            <h1 className="text-xl font-extrabold text-white">Client Portfolio Health</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Blended ROAS, active creative breakdown, and account statuses across all client accounts.
          </p>
        </div>

        <Button variant="primary" size="sm" onClick={handleOpenAdd}>
          <Plus className="w-4 h-4 mr-1" />
          <span>Add New Client</span>
        </Button>
      </div>

      <ClientCardsGrid
        clients={clients}
        isLoading={isLoading}
        onEditClient={handleEditClient}
        onSyncClient={handleSyncClient}
      />

      <ClientFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        client={selectedClientForEdit}
      />
    </div>
  );
};
