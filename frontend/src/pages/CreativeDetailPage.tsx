import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCreativeDetail, useCreativeTrend, useCreativeSnapshots, useClients } from '../api/queries';
import { CreativeHeader } from '../components/creative/CreativeHeader';
import { CreativeTrendChart } from '../components/creative/CreativeTrendChart';
import { CreativeSnapshotTable } from '../components/creative/CreativeSnapshotTable';
import { CreativeEditModal } from '../components/creative/CreativeEditModal';

export const CreativeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isEditOpen, setIsEditOpen] = useState(false);

  const { data: creative, isLoading: isLoadingCreative } = useCreativeDetail(id);
  const { data: trendData, isLoading: isLoadingTrend } = useCreativeTrend(id, 30);
  const { data: snapshots = [], isLoading: isLoadingSnapshots } = useCreativeSnapshots(id, 30);
  const { data: clients = [] } = useClients();

  if (isLoadingCreative) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 py-12 text-center text-xs font-mono text-slate-400">
        Loading creative details...
      </div>
    );
  }

  if (!creative) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 py-12 text-center">
        <h3 className="text-base font-bold text-slate-200">Creative Not Found</h3>
        <button
          onClick={() => navigate('/')}
          className="mt-3 text-xs text-amber-400 hover:underline font-semibold"
        >
          ← Return to Leaderboard
        </button>
      </div>
    );
  }

  const client = clients.find((c) => c._id === creative.client_id);
  const latestSnapshot = snapshots[0];

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Creative Header */}
      <CreativeHeader
        creative={creative}
        latestSnapshot={latestSnapshot}
        targetRoas={client?.target_roas || 2.5}
        onBack={() => navigate('/')}
        onEdit={() => setIsEditOpen(true)}
      />

      {/* 30-Day Trendline Recharts Chart */}
      <CreativeTrendChart
        data={trendData?.data_points || []}
        targetRoas={trendData?.target_roas || 2.5}
        isLoading={isLoadingTrend}
      />

      {/* Immutable Daily Snapshots History */}
      <CreativeSnapshotTable
        snapshots={snapshots}
        isLoading={isLoadingSnapshots}
      />

      {/* Manual Edit Modal */}
      <CreativeEditModal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        creative={creative}
      />
    </div>
  );
};
