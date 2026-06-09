export function ResultList({ results, loading }: { results: any[]; loading?: boolean }) {
  if (loading) return <div className="text-center py-8">🐼 胖达正在翻找数据...</div>
  if (results.length === 0) return <div className="text-center py-8 text-gray-500">请输入关键词开始搜索</div>
  return (
    <div className="space-y-4">
      {results.map((item) => (
        <div key={item.id} className="bg-white rounded-lg shadow p-4">
          <h3 className="font-medium">{item.title}</h3>
          <p className="text-gray-500 text-sm">{item.description}</p>
        </div>
      ))}
    </div>
  )
}