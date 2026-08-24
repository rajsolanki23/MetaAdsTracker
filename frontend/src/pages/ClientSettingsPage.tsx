import React, { useState } from 'react';
import { useClients } from '../api/queries';
import { Client } from '../types';
import { ClientFormModal } from '../components/clients/ClientFormModal';
import { Button } from '../components/ui/Button';
import { Settings, Plus, Edit2, ShieldCheck, ShieldAlert } from 'lucide-react';

export const ClientSettingsPage: React.FC = () => {
  const { data: clients = [] } = useClients();
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenAdd = () => {
    setSelectedClient(null);
    setIsModalOpen(true);
  };

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setIsModalOpen(true);
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-amber-400" />
            <h1 className="text-xl font-extrabold text-white">Client Account Settings</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Configure target ROAS rules, minimum spend thresholds, currencies, and ad account bindings.
          </p>
        </div>

        <Button variant="primary" size="sm" onClick={handleOpenAdd}>
          <Plus className="w-4 h-4 mr-1" />
          <span>Add Client</span>
        </Button>
      </div>

      <div className="bg-[#0f172a]/95 border border-slate-800 rounded-2xl overflow-hidden shadow-xl backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] uppercase text-slate-400 bg-slate-900/60">
                <th className="py-3 px-4">Client Name</th>
                <th className="py-3 px-3">Meta Account ID</th>
                <th className="py-3 px-3 text-right">Target ROAS</th>
                <th className="py-3 px-3 text-right">Min Spend</th>
                <th className="py-3 px-3 text-center">Currency</th>
                <th className="py-3 px-3">Timezone</th>
                <th className="py-3 px-3 text-center">Meta Status</th>
                <th className="py-3 pr-4 pl-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {clients.map((c) => (
                <tr key={c._id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-100 font-sans text-sm">
                    {c.name}
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    {c.meta_account_id || <span className="text-slate-500 italic">Not set</span>}
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-400">
                    {c.target_roas.toFixed(1)}x
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-slate-200">
                    ${c.min_spend_threshold.toFixed(2)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {c.currency}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">
                    {c.timezone}
                  </td>
                  <td className="py-3 px-3 text-center">
                    {c.access_token ? (
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-[10px] font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Connected
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-slate-500 text-[10px]">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        Manual
                      </span>
                    )}
                  </td>
                  <td className="py-3 pr-4 pl-2 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(c)}
                      className="text-xs"
                    >
                      <Edit2 className="w-3.5 h-3.5 mr-1" />
                      <span>Edit</span>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <ClientFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        client={selectedClient}
      />
    </div>
  );
};
