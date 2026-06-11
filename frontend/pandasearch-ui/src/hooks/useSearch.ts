import { useState, useCallback } from 'react';
import { search as searchApi } from '../services/api';
import { SearchResultItem, FilterOption } from '../types/search';

export function useSearch() {
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [aiSummary, setAiSummary] = useState('');
  const [total, setTotal] = useState(0);
  const [suggestedFilters, setSuggestedFilters] = useState<FilterOption[]>([]);
  const [tookMs, setTookMs] = useState(0);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState('');

  const executeSearch = useCallback(
    async (params: {
      query: string;
      filters?: Record<string, any>;
      sort_by?: string;
      page?: number;
      page_size?: number;
      append?: boolean;
    }) => {
      setLoading(true);
      try {
        const data = await searchApi({
          query: params.query,
          filters: params.filters,
          sort_by: params.sort_by,
          page: params.page ?? 1,
          page_size: params.page_size ?? 20,
        });
        setQuery(data.query);
        setTotal(data.total);
        setAiSummary(data.ai_summary || '');
        setSuggestedFilters(data.suggested_filters || []);
        setTookMs(data.took_ms || 0);
        setPage(data.page);
        if (params.append) {
          setResults((prev) => [...prev, ...data.results]);
        } else {
          setResults(data.results);
        }
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    results,
    loading,
    aiSummary,
    total,
    suggestedFilters,
    tookMs,
    page,
    query,
    executeSearch,
  };
}
