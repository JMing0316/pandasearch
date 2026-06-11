interface EmptyStateProps {
  hasSearched?: boolean;
}

export function EmptyState({ hasSearched }: EmptyStateProps) {
  return (
    <div className="text-center py-16">
      <div className="text-5xl mb-4">{hasSearched ? '😿' : '🐼'}</div>
      <div className="text-gray-500 text-lg">
        {hasSearched ? '没有找到相关结果，换个关键词试试？' : '请输入关键词开始搜索'}
      </div>
    </div>
  );
}
