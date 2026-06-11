import { SortOption } from '../../types/search';
import { ArrowUpDown } from 'lucide-react';

interface SortBarProps {
  sortOptions: SortOption[];
  currentSort: string;
  onSortChange: (sort: string) => void;
  total: number;
  tookMs: number;
}

export function SortBar({ sortOptions, currentSort, onSortChange, total, tookMs }: SortBarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 bg-white rounded-xl shadow border border-gray-100 px-4 py-3">
      <div className="flex items-center gap-2">
        <ArrowUpDown className="w-4 h-4 text-gray-400" />
        <span className="text-sm text-gray-500">排序</span>
        <select
          value={currentSort}
          onChange={(e) => onSortChange(e.target.value)}
          className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:border-blue-400"
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="text-sm text-gray-500">
        共 <span className="font-medium text-gray-800">{total}</span> 条结果
        {tookMs > 0 && (
          <span className="ml-2 text-gray-400">({tookMs}ms)</span>
        )}
      </div>
    </div>
  );
}
