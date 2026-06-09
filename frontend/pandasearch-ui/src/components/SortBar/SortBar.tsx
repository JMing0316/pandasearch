export function SortBar() {
  return (
    <div className="flex items-center justify-between mb-4">
      <span className="text-sm text-gray-500">排序</span>
      <select className="text-sm border rounded px-2 py-1">
        <option>相关性</option>
        <option>价格从低到高</option>
        <option>价格从高到低</option>
        <option>评分最高</option>
      </select>
    </div>
  )
}