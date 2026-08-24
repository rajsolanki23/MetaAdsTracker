import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from './client';
import {
  Client,
  LeaderboardItem,
  Creative,
  DailySnapshot,
  SyncLog,
  CreativeTrendResponse,
  BulkImportPreviewResponse,
} from '../types';

export interface LeaderboardParams {
  client_id?: string;
  statuses?: string;
  target_date?: string;
  min_spend?: number;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
}

// 1. Leaderboard Queries
export function useLeaderboard(params: LeaderboardParams) {
  return useQuery({
    queryKey: ['leaderboard', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params.client_id) searchParams.set('client_id', params.client_id);
      if (params.statuses) searchParams.set('statuses', params.statuses);
      if (params.target_date) searchParams.set('target_date', params.target_date);
      if (params.min_spend !== undefined && params.min_spend > 0) searchParams.set('min_spend', params.min_spend.toString());
      if (params.search) searchParams.set('search', params.search);
      if (params.sort_by) searchParams.set('sort_by', params.sort_by);
      if (params.sort_dir) searchParams.set('sort_dir', params.sort_dir);

      const qs = searchParams.toString();
      return fetchApi<LeaderboardItem[]>(`/leaderboard${qs ? `?${qs}` : ''}`);
    },
    refetchInterval: 30000, // 30s auto-refresh
  });
}

export function usePodiumTop3(clientId?: string, targetDate?: string) {
  return useQuery({
    queryKey: ['podium', clientId, targetDate],
    queryFn: () => {
      const sp = new URLSearchParams();
      if (clientId) sp.set('client_id', clientId);
      if (targetDate) sp.set('target_date', targetDate);
      const qs = sp.toString();
      return fetchApi<LeaderboardItem[]>(`/leaderboard/podium${qs ? `?${qs}` : ''}`);
    },
  });
}

// 2. Client Queries & Mutations
export function useClients() {
  return useQuery({
    queryKey: ['clients'],
    queryFn: () => fetchApi<Client[]>('/clients'),
  });
}

export function useClientDetail(clientId?: string) {
  return useQuery({
    queryKey: ['client', clientId],
    queryFn: () => fetchApi<Client>(`/clients/${clientId}`),
    enabled: Boolean(clientId),
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Client>) =>
      fetchApi<Client>('/clients', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
  });
}

export function useUpdateClient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Client> }) =>
      fetchApi<Client>(`/clients/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['client'] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
  });
}

export function useDeleteClient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      fetchApi<{ status: string; client_id: string }>(`/clients/${id}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
  });
}

// 3. Creative Detail Queries & Mutations
export function useCreativeDetail(creativeId?: string) {
  return useQuery({
    queryKey: ['creative', creativeId],
    queryFn: () => fetchApi<Creative>(`/creatives/${creativeId}`),
    enabled: Boolean(creativeId),
  });
}

export function useCreativeTrend(creativeId?: string, days = 30) {
  return useQuery({
    queryKey: ['creative-trend', creativeId, days],
    queryFn: () => fetchApi<CreativeTrendResponse>(`/creatives/${creativeId}/trend?days=${days}`),
    enabled: Boolean(creativeId),
  });
}

export function useCreativeSnapshots(creativeId?: string, days = 30) {
  return useQuery({
    queryKey: ['creative-snapshots', creativeId, days],
    queryFn: () => fetchApi<DailySnapshot[]>(`/creatives/${creativeId}/snapshots?days=${days}`),
    enabled: Boolean(creativeId),
  });
}

export function useCreateCreative() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Creative>) =>
      fetchApi<Creative>('/creatives', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}

export function useUpdateCreative() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Creative> }) =>
      fetchApi<Creative>(`/creatives/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['creative', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
  });
}

// 4. Meta Sync Queries & Mutations
export function useSyncLogs(limit = 50, clientId?: string) {
  return useQuery({
    queryKey: ['sync-logs', limit, clientId],
    queryFn: () => {
      const sp = new URLSearchParams();
      sp.set('limit', limit.toString());
      if (clientId) sp.set('client_id', clientId);
      return fetchApi<SyncLog[]>(`/meta/logs?${sp.toString()}`);
    },
  });
}

export function useTestMetaConnection() {
  return useMutation({
    mutationFn: (data: { meta_account_id: string; access_token: string }) =>
      fetchApi<{ valid: boolean; account_id: string; account_name: string; currency: string }>('/meta/test-connection', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useTriggerClientSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ clientId, targetDate }: { clientId: string; targetDate?: string }) => {
      const qs = targetDate ? `?target_date=${targetDate}` : '';
      return fetchApi<{ status: string; records_synced: number }>(`/meta/sync/${clientId}${qs}`, {
        method: 'POST',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['sync-logs'] });
    },
  });
}

export function useTriggerAllSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      fetchApi<{ status: string; total_clients: number }>('/meta/sync-all', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['sync-logs'] });
    },
  });
}

// 5. Bulk Import Queries & Mutations
export function useBulkImportPreview() {
  return useMutation({
    mutationFn: (data: { client_id: string; raw_text: string }) =>
      fetchApi<BulkImportPreviewResponse>('/import/preview', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useCommitBulkImport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { client_id: string; rows: any[]; target_date?: string }) =>
      fetchApi<{ success: boolean; total_processed: number; created_creatives: number }>('/import/bulk-paste', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}
