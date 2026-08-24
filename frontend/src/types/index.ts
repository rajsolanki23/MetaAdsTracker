export type StatusType = 'WIN' | 'LOSS' | 'TESTING' | 'PAUSED';

export interface Client {
  _id: string;
  name: string;
  meta_account_id?: string;
  access_token?: string;
  target_roas: number;
  min_spend_threshold: number;
  currency: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_sync_at?: string;
  last_sync_status?: string;
  last_sync_error?: string;
  blended_spend: number;
  blended_revenue: number;
  blended_roas: number;
  active_creatives_count: number;
  wins_count: number;
  losses_count: number;
  testing_count: number;
  paused_count: number;
  best_creative_name?: string;
  best_creative_roas?: number;
  worst_creative_name?: string;
  worst_creative_roas?: number;
  health_status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
}

export interface Creative {
  _id: string;
  client_id: string;
  name: string;
  meta_creative_id?: string;
  meta_ad_id?: string;
  thumbnail_url?: string;
  body_copy?: string;
  headline?: string;
  call_to_action?: string;
  status_override?: string;
  notes?: string;
  tags: string[];
  first_seen_date: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface DailySnapshot {
  _id: string;
  creative_id: string;
  client_id: string;
  date: string;
  spend: number;
  revenue: number;
  purchases: number;
  impressions: number;
  clicks: number;
  roas: number;
  ctr: number;
  cpa: number;
  status: StatusType;
  streak: number;
  rank?: number;
  rank_movement?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaderboardItem {
  id: string;
  name: string;
  thumbnail_url?: string;
  client_id: string;
  client_name: string;
  target_roas: number;
  min_spend_threshold: number;
  spend: number;
  revenue: number;
  purchases: number;
  impressions: number;
  clicks: number;
  roas: number;
  ctr: number;
  cpa: number;
  days_live: number;
  status: StatusType;
  streak: number;
  rank: number;
  yesterday_rank?: number;
  rank_movement: string;
  rank_movement_val: number;
  first_seen_date: string;
  headline?: string;
  body_copy?: string;
  tags: string[];
  notes?: string;
}

export interface SyncLog {
  _id: string;
  client_id?: string;
  client_name?: string;
  status: 'SUCCESS' | 'PARTIAL' | 'FAILED';
  records_synced: number;
  duration_ms: number;
  error_message?: string;
  sync_type: 'SCHEDULED' | 'MANUAL' | 'BULK_IMPORT';
  timestamp: string;
}

export interface TrendPoint {
  date: string;
  spend: number;
  revenue: number;
  roas: number;
  cpa: number;
  ctr: number;
  target_roas: number;
  status: StatusType;
  streak: number;
}

export interface CreativeTrendResponse {
  creative_id: string;
  creative_name: string;
  target_roas: number;
  data_points: TrendPoint[];
}

export interface BulkImportPreviewRow {
  name: string;
  spend: number;
  revenue: number;
  purchases: number;
  impressions: number;
  clicks: number;
  roas: number;
  ctr: number;
  cpa: number;
  thumbnail_url?: string;
  evaluated_status: StatusType;
  errors?: string[];
}

export interface BulkImportPreviewResponse {
  valid: boolean;
  total_rows: number;
  rows: BulkImportPreviewRow[];
  target_roas: number;
  min_spend_threshold: number;
  error?: string;
}
