export interface Tender {
  id: string;
  ifb_no: string;
  title: string;
  organization: string;
  deadline: string;
  procurement_type: string;
  notice_date: string;
  province: string | null;
  source: string;
  days_left: number | null;
  scraped_date: string;
  marked_relevant: boolean;
  created_at: string;
  updated_at: string;
}

export interface TenderFilter {
  keyword?: string;
  organization?: string[];
  procurement_type?: string[];
  date_from?: string;
  date_to?: string;
  days_left_min?: number;
  days_left_max?: number;
  province?: string[];
  source?: string[];
}

export interface ScrapingStatus {
  status: 'idle' | 'scraping' | 'completed' | 'failed';
  current_page?: number;
  total_pages?: number;
  tenders_found?: number;
  duplicates_skipped?: number;
  current_url?: string;
  error_message?: string;
  last_scraped?: string;
}

export interface ExportOptions {
  export_type: 'relevant' | 'all' | 'filtered' | 'selected';
  selected_columns: string[];
  include_summary: boolean;
  sort_by?: 'deadline' | 'organization' | 'days_left';
}

export interface AuditLogEntry {
  id: string;
  action_type: string;
  details: Record<string, unknown>;
  tender_count: number | null;
  created_at: string;
}

export interface FilterPreset {
  id: string;
  name: string;
  filter_config: TenderFilter;
  created_at: string;
}
