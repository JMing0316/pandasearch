import { useState, useEffect, useCallback } from 'react';
import { SearchBox } from './components/SearchBox';
import { ResultList } from './components/ResultList';
import { FilterPanel } from './components/FilterPanel';
import { SortBar } from './components/SortBar';
import { AISummary } from './components/AISummary';
import { useSearch } from './hooks/useSearch';
import { getConfig } from './services/api';
import { SearchConfig } from './types/search';

function useConfig() {
  const [config, setConfig] = useState<SearchConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getConfig()
      .then((data) => {
        setConfig(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { config, loading, error };
}

function App() {
  const {
    results,
    loading,
    aiSummary,
    total,
    suggestedFilters,
    tookMs,
    page,
    executeSearch,
  } = useSearch();

  const { config, loading: configLoading } = useConfig();
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [sortBy, setSortBy] = useState<string>('');
  const [hasSearched, setHasSearched] = useState(false);

  // Initialize default sort from config
  useEffect(() => {
    if (config?.behavior?.default_sort) {
      setSortBy(config.behavior.default_sort);
    }
  }, [config]);

  const doSearch = useCallback(
    (params: {
      query?: string;
      filters?: Record<string, any>;
      sort_by?: string;
      page?: number;
      append?: boolean;
    }) => {
      const q = params.query !== undefined ? params.query : query;
      if (!q.trim()) return;
      setQuery(q);
      setHasSearched(true);
      executeSearch({
        query: q,
        filters: params.filters !== undefined ? params.filters : filters,
        sort_by: params.sort_by !== undefined ? params.sort_by : sortBy,
        page: params.page ?? 1,
        page_size: config?.behavior?.page_size ?? 20,
        append: params.append,
      });
    },
    [query, filters, sortBy, config, executeSearch]
  );

  const handleSearch = useCallback(
    (q: string) => {
      setFilters({});
      doSearch({ query: q, filters: {}, sort_by: sortBy, page: 1 });
    },
    [doSearch, sortBy]
  );

  const handleFilterChange = useCallback(
    (newFilters: Record<string, any>) => {
      setFilters(newFilters);
      doSearch({ filters: newFilters, page: 1 });
    },
    [doSearch]
  );

  const handleSortChange = useCallback(
    (newSort: string) => {
      setSortBy(newSort);
      doSearch({ sort_by: newSort, page: 1 });
    },
    [doSearch]
  );

  const handleLoadMore = useCallback(() => {
    doSearch({ page: page + 1, append: true });
  }, [doSearch, page]);

  const sortOptions = config?.behavior?.sort_options || [
    { value: 'relevance', label: '相关性' },
    { value: 'price_asc', label: '价格从低到高' },
    { value: 'price_desc', label: '价格从高到低' },
    { value: 'rating', label: '评分最高' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <span className="text-2xl">🐼</span>
          <h1 className="text-xl font-bold text-gray-800">PandaSearch</h1>
          <span className="text-sm text-gray-500">胖达搜索</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Box */}
        <div className="max-w-2xl mx-auto mb-8">
          <SearchBox onSearch={handleSearch} loading={loading} />
        </div>

        {/* AI Summary */}
        {aiSummary && <AISummary summary={aiSummary} />}

        <div className="flex gap-6">
          {/* Filter Panel */}
          <aside className="w-64 flex-shrink-0">
            {configLoading ? (
              <div className="bg-white rounded-xl shadow border border-gray-100 p-4 text-sm text-gray-400">
                加载配置中...
              </div>
            ) : (
              <FilterPanel
                filters={suggestedFilters}
                appliedFilters={filters}
                onFilterChange={handleFilterChange}
              />
            )}
          </aside>

          {/* Results */}
          <div className="flex-1">
            {hasSearched && (
              <SortBar
                sortOptions={sortOptions}
                currentSort={sortBy || config?.behavior?.default_sort || 'relevance'}
                onSortChange={handleSortChange}
                total={total}
                tookMs={tookMs}
              />
            )}
            <ResultList
              results={results}
              loading={loading}
              config={config || undefined}
              hasSearched={hasSearched}
            />

            {/* Load more */}
            {hasSearched && results.length > 0 && results.length < total && (
              <div className="mt-6 text-center">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="px-6 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-300 disabled:opacity-50 transition-colors shadow-sm"
                >
                  {loading ? '🐼 加载中...' : '加载更多'}
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
