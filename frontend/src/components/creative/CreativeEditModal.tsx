import React, { useState, useEffect } from 'react';
import { Creative } from '../../types';
import { Dialog } from '../ui/Dialog';
import { Input, Select } from '../ui/Input';
import { Button } from '../ui/Button';
import { useUpdateCreative } from '../../api/queries';
import { useToast } from '../ui/Toast';

interface CreativeEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  creative: Creative;
}

export const CreativeEditModal: React.FC<CreativeEditModalProps> = ({
  isOpen,
  onClose,
  creative,
}) => {
  const [name, setName] = useState('');
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  const [headline, setHeadline] = useState('');
  const [bodyCopy, setBodyCopy] = useState('');
  const [statusOverride, setStatusOverride] = useState('');
  const [notes, setNotes] = useState('');
  const [tagsStr, setTagsStr] = useState('');

  const updateCreative = useUpdateCreative();
  const { showToast } = useToast();

  useEffect(() => {
    if (creative) {
      setName(creative.name);
      setThumbnailUrl(creative.thumbnail_url || '');
      setHeadline(creative.headline || '');
      setBodyCopy(creative.body_copy || '');
      setStatusOverride(creative.status_override || '');
      setNotes(creative.notes || '');
      setTagsStr(creative.tags.join(', '));
    }
  }, [creative, isOpen]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const tags = tagsStr
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    try {
      await updateCreative.mutateAsync({
        id: creative._id,
        data: {
          name: name.trim(),
          thumbnail_url: thumbnailUrl.trim() || undefined,
          headline: headline.trim() || undefined,
          body_copy: bodyCopy.trim() || undefined,
          status_override: statusOverride || undefined,
          notes: notes.trim() || undefined,
          tags,
        },
      });
      showToast('Creative updated successfully!', 'success');
      onClose();
    } catch (err: any) {
      showToast(err.message || 'Failed to update creative', 'error');
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Edit Creative Metadata"
      description="Update copy, tags, thumbnail, or apply a manual status override."
      maxWidth="lg"
    >
      <form onSubmit={handleSave} className="space-y-4">
        <Input
          label="Creative Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <Input
          label="Thumbnail Image URL"
          placeholder="https://..."
          value={thumbnailUrl}
          onChange={(e) => setThumbnailUrl(e.target.value)}
        />

        <Input
          label="Headline"
          placeholder="e.g. Transform Your Routine"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
        />

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Primary Ad Copy
          </label>
          <textarea
            value={bodyCopy}
            onChange={(e) => setBodyCopy(e.target.value)}
            rows={3}
            className="w-full px-3.5 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-400"
            placeholder="Ad copy text..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Manual Status Override"
            value={statusOverride}
            onChange={(e) => setStatusOverride(e.target.value)}
            options={[
              { value: '', label: 'Auto (Calculate from Rules)' },
              { value: 'PAUSED', label: 'PAUSED (Manually Paused)' },
              { value: 'WIN', label: 'WIN (Force Win)' },
              { value: 'LOSS', label: 'LOSS (Force Loss)' },
              { value: 'TESTING', label: 'TESTING (Force Testing)' },
            ]}
          />

          <Input
            label="Tags (comma-separated)"
            placeholder="UGC, Video, Scale"
            value={tagsStr}
            onChange={(e) => setTagsStr(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Operator Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            className="w-full px-3.5 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-400"
            placeholder="Notes about creative iterations, hooks, audiences..."
          />
        </div>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" isLoading={updateCreative.isPending}>
            Save Changes
          </Button>
        </div>
      </form>
    </Dialog>
  );
};
