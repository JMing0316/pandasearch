export interface SearchResultItem {
  id: string | number;
  score: number;
  highlights?: Record<string, string>;
  [key: string]: any;
}

export interface FilterOption {
  field: string;
  type: 'multi_select' | 'range' | 'rating' | 'boolean';
  label: string;
  options?: Array<{ value: string; count?: number }>;
  min?: number;
  max?: number;
}

export interface SearchResponse {
  results: SearchResultItem[];
  total: number;
  page: number;
  page_size: number;
  query: string;
  ai_summary?: string;
  suggested_filters: FilterOption[];
  took_ms: number;
}

export interface SortOption {
  value: string;
  label: string;
}

export interface SearchConfig {
  table: string;
  fields: Record<string, any>;
  search: any;
  presentation: any;
  behavior: {
    sort_options: SortOption[];
    default_sort: string;
    page_size: number;
  };
}
