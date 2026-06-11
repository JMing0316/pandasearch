import { SearchResultItem, SearchConfig } from '../../types/search';
import { ResultCard } from '../ResultCard';
import { EmptyState } from '../EmptyState';

interface ResultListProps {
  results: SearchResultItem[];
  loading?: boolean;
  config?: SearchConfig;
  hasSearched?: boolean;
}

export function ResultList({ results, loading, config, hasSearched }: ResultListProps) {
  if (loading && results.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4 animate-bounce">🐼</div>
        <div className="text-gray-500 text-lg">胖达正在翻找数据...</div>
      </div>
    );
  }

  if (results.length === 0) {
    return <EmptyState hasSearched={hasSearched} />;
  }

  return (
    <div className="space-y-4">
      {results.map((item) => (
        <ResultCard key={item.id} item={item} config={config} />
      ))}
      {loading && results.length > 0 && (
        <div className="text-center py-4 text-gray-400">🐼 加载更多中...</div>
      )}
    </div>
  );
}
