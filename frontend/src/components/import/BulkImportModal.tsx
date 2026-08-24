import React, { useState } from 'react';
import { Client, BulkImportPreviewRow } from '../../types';
import { Dialog } from '../ui/Dialog';
import { Select } from '../ui/Input';
import { Button } from '../ui/Button';
import { StatusBadge } from '../ui/Badge';
import { useBulkImportPreview, useCommitBulkImport } from '../../api/queries';
import { useToast } from '../ui/Toast';
import { CheckCircle2, ArrowRight } from 'lucide-react';

interface BulkImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  clients: Client[];
  defaultClientId?: string;
}

export const BulkImportModal: React.FC<BulkImportModalProps> = ({
  isOpen,
  onClose,
  clients,
  defaultClientId,
}) => {
  const [clientId, setClientId] = useState(defaultClientId || (clients[0]?._id || ''));
  const [rawText, setRawText] = useState('');
  const [previewRows, setPreviewRows] = useState<BulkImportPreviewRow[]>([]);
  const [step, setStep] = useState<'paste' | 'preview'>('paste');

  const previewMutation = useBulkImportPreview();
  const commitMutation = useCommitBulkImport();
  const { showToast } = useToast();

  const handlePreview = async () => {
    if (!clientId) {
      showToast('Please select a client account', 'error');
      return;
    }
    if (!rawText.trim()) {
      showToast('Please paste your CSV or TSV table data', 'error');
      return;
    }

    try {
      const res = await previewMutation.mutateAsync({
        client_id: clientId,
        raw_text: rawText,
      });
      setPreviewRows(res.rows);
      setStep('preview');
      showToast(`Parsed ${res.total_rows} rows successfully!`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to parse table data', 'error');
    }
  };

  const handleCommit = async () => {
    if (!clientId || previewRows.length === 0) return;

    try {
      const res = await commitMutation.mutateAsync({
        client_id: clientId,
        rows: previewRows,
      });
      showToast(
        `Imported ${res.total_processed} creatives (${res.created_creatives} new created)!`,
        'success'
      );
      setStep('paste');
      setRawText('');
      setPreviewRows([]);
      onClose();
    } catch (err: any) {
      showToast(err.message || 'Failed to import rows', 'error');
    }
  };

  const sampleCsv = `Ad Name\tAmount Spent\tPurchase ROAS\tWebsite Purchases\tImpressions\tLink Clicks
"Winner Video Hook 1"\t$450.00\t3.85\t28\t18,000\t450
"Founder UGC Story"\t$280.00\t2.95\t14\t11,000\t280
"Product Comparison Static"\t$190.00\t1.40\t5\t8,500\t120
"New Hook Test #5"\t$40.00\t1.80\t1\t1,400\t25`;

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Bulk Paste Import (Ads Manager Backup)"
      description="Paste exported columns from Meta Ads Manager to update or add creatives offline."
      maxWidth="4xl"
    >
      <div className="space-y-4">
        <Select
          label="Target Client Account"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
          options={clients.map((c) => ({ value: c._id, label: `${c.name} (${c.currency})` }))}
        />

        {step === 'paste' ? (
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Paste CSV / Tab-Separated Data from Ads Manager
              </label>
              <button
                type="button"
                onClick={() => setRawText(sampleCsv)}
                className="text-[11px] font-mono text-amber-400 hover:underline"
              >
                Load Sample Data
              </button>
            </div>
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows={10}
              className="w-full p-3.5 bg-slate-900 font-mono text-xs text-slate-100 border border-slate-700/80 rounded-xl focus:outline-none focus:border-amber-400 placeholder:text-slate-600"
              placeholder="Paste table columns (Ad Name, Amount Spent, Purchases, Purchase ROAS, Impressions, Clicks)..."
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Supports copied cells directly from Ads Manager or CSV exports. Automatically calculates ROAS, CTR, CPA, and Status.
            </p>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handlePreview}
                isLoading={previewMutation.isPending}
              >
                <span>Preview Table</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase text-slate-300 font-mono">
                Preview ({previewRows.length} Creatives Ready)
              </span>
              <button
                onClick={() => setStep('paste')}
                className="text-xs text-amber-400 hover:underline font-semibold"
              >
                ← Edit Pasted Text
              </button>
            </div>

            <div className="max-h-80 overflow-y-auto border border-slate-800 rounded-xl">
              <table className="w-full text-left border-collapse text-xs font-mono">
                <thead>
                  <tr className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800 sticky top-0">
                    <th className="py-2.5 px-3">Creative Name</th>
                    <th className="py-2.5 px-2 text-right">Spend</th>
                    <th className="py-2.5 px-2 text-right">ROAS</th>
                    <th className="py-2.5 px-2 text-right">Purchases</th>
                    <th className="py-2.5 px-2 text-right">CTR</th>
                    <th className="py-2.5 px-2 text-right">CPA</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {previewRows.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="py-2 px-3 font-semibold text-slate-200 truncate max-w-xs">{r.name}</td>
                      <td className="py-2 px-2 text-right text-slate-300">${r.spend.toFixed(2)}</td>
                      <td className="py-2 px-2 text-right font-bold text-emerald-400">{r.roas.toFixed(2)}x</td>
                      <td className="py-2 px-2 text-right text-slate-300">{r.purchases}</td>
                      <td className="py-2 px-2 text-right text-slate-300">{r.ctr.toFixed(2)}%</td>
                      <td className="py-2 px-2 text-right text-slate-300">${r.cpa.toFixed(2)}</td>
                      <td className="py-2 px-3 text-center">
                        <StatusBadge status={r.evaluated_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-2">
              <Button variant="ghost" size="sm" onClick={() => setStep('paste')}>
                Back to Edit
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleCommit}
                isLoading={commitMutation.isPending}
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                <span>Commit & Save {previewRows.length} Creatives</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  );
};
