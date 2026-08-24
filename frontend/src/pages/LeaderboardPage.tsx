import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useLeaderboard, usePodiumTop3, useClients } from '../api/queries';
import { StatusType } from '../types';
import { PodiumTop3 } from '../components/leaderboard/PodiumTop3';
import { LeaderboardFilters } from '../components/leaderboard/LeaderboardFilters';
import { LeaderboardTable } from '../components/leaderboard/LeaderboardTable';

export const LeaderboardPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const clientId = searchParams.get('client_id') || '';
  const [selectedStatuses, setSelectedStatuses] = useState<StatusType[]>([]);
  const [minSpend, setMinSpend] = useState<number>(0);
  const [search, setSearch] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('roas');
  const [sortDir, setSortDir] = useState<string>('desc');

  const { data: clients = [] } = useClients();

  const handleSelectClient = (id: string) => {
    if (id) {
      setSearchParams({ client_id: id });
    } else {
      setSearchParams({});
    }
  };

  const handleToggleStatus = (status: StatusType) => {
    setSelectedStatuses((prev) =>
      prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]
    );
  };

  const handleToggleSortDir = () => {
    setSortDir((prev) => (prev === 'desc' ? 'asc' : 'desc'));
  };

  const handleResetFilters = () => {
    setSelectedStatuses([]);
    setMinSpend(0);
    setSearch('');
    setSortBy('roas');
    setSortDir('desc');
    setSearchParams({});
  };

  const leaderboardQuery = useLeaderboard({
    client_id: clientId || undefined,
    statuses: selectedStatuses.length > 0 ? selectedStatuses.join(',') : undefined,
    min_spend: minSpend > 0 ? minSpend : undefined,
    search: search.trim() || undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  const podiumQuery = usePodiumTop3(clientId || undefined);

  const handleSelectCreative = (id: string) => {
    navigate(`/creatives/${id}`);
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Top 3 Champions Podium */}
      <PodiumTop3
        items={podiumQuery.data || []}
        onSelectCreative={handleSelectCreative}
      />

      {/* Interactive Filters Bar */}
      <LeaderboardFilters
        clients={clients}
        selectedClientId={clientId}
        onSelectClient={handleSelectClient}
        selectedStatuses={selectedStatuses}
        onToggleStatus={handleToggleStatus}
        minSpend={minSpend}
        onChangeMinSpend={setMinSpend}
        search={search}
        onChangeSearch={setSearch}
        sortBy={sortBy}
        onChangeSortBy={setSortBy}
        sortDir={sortDir}
        onToggleSortDir={handleToggleSortDir}
        onResetFilters={handleResetFilters}
      />

      {/* Main Leaderboard Table */}
      <LeaderboardTable
        items={leaderboardQuery.data || []}
        isLoading={leaderboardQuery.isLoading}
        onSelectCreative={handleSelectCreative}
      />
    </div>
  );
};
