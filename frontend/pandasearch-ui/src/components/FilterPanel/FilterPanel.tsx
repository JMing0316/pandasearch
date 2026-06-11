import { useState, useCallback } from 'react';
import { FilterOption } from '../../types/search';
import { Star, X, SlidersHorizontal } from 'lucide-react';

interface FilterPanelProps {
  filters: FilterOption[];
  appliedFilters: Record<string, any>;
  onFilterChange: (filters: Record<string, any>) => void;
}

export function FilterPanel({ filters, appliedFilters, onFilterChange }: FilterPanelProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState<Record<string, any>>(appliedFilters);

  const updateFilter = useCallback((field: string, value: any) => {
    setLocalFilters((prev) => {
      const next = { ...prev };
      if (value === undefined || value === null || (Array.isArray(value) && value.length === 0)) {
        delete next[field];
      } else {
        next[field] = value;
      }
      onFilterChange(next);
      return next;
    });
  }, [onFilterChange]);

  const clearAll = useCallback(() => {
    setLocalFilters({});
    onFilterChange({});
  }, [onFilterChange]);

  const hasFilters = Object.keys(localFilters).length > 0;

  return (
    <div>
      {/* Mobile toggle */}
      <button
        className="lg:hidden flex items-center gap-2 w-full bg-white rounded-lg shadow px-4 py-3 mb-4 text-gray-700"
        onClick={() => setMobileOpen((o) => !o)}
      >
        <SlidersHorizontal className="w-4 h-4" />
        <span>筛选器</span>
        {hasFilters && (
          <span className="ml-auto bg-blue-500 text-white text-xs rounded-full px-2 py-0.5">
            {Object.keys(localFilters).length}
          </span>
        )}
      </button>

      <div className={`${mobileOpen ? 'block' : 'hidden'} lg:block bg-white rounded-xl shadow border border-gray-100`}>
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">筛选器</h3>
          {hasFilters && (
            <button
              onClick={clearAll}
              className="text-xs text-blue-500 hover:text-blue-600 flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              清除筛选
            </button>
          )}
        </div>

        <div className="p-4 space-y-6">
          {filters.length === 0 && (
            <p className="text-sm text-gray-400">暂无可用筛选器</p>
          )}

          {filters.map((filter) => (
            <div key={filter.field}>
              <h4 className="text-sm font-medium text-gray-700 mb-2">{filter.label}</h4>

              {filter.type === 'multi_select' && (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {filter.options?.map((opt) => {
                    const current = (localFilters[filter.field] as string[]) || [];
                    const checked = current.includes(opt.value);
                    return (
                      <label
                        key={opt.value}
                        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                          checked={checked}
                          onChange={() => {
                            const next = checked
                              ? current.filter((v) => v !== opt.value)
                              : [...current, opt.value];
                            updateFilter(filter.field, next.length ? next : undefined);
                          }}
                        />
                        <span className="flex-1">{opt.value}</span>
                        {opt.count !== undefined && (
                          <span className="text-xs text-gray-400">({opt.count})</span>
                        )}
                      </label>
                    );
                  })}
                </div>
              )}

              {filter.type === 'range' && (
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    placeholder={filter.min !== undefined ? String(filter.min) : '最小'}
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                    value={localFilters[filter.field]?.min ?? ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : Number(e.target.value);
                      const current = localFilters[filter.field] || {};
                      updateFilter(filter.field, { ...current, min: val });
                    }}
                  />
                  <span className="text-gray-400">-</span>
                  <input
                    type="number"
                    placeholder={filter.max !== undefined ? String(filter.max) : '最大'}
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                    value={localFilters[filter.field]?.max ?? ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : Number(e.target.value);
                      const current = localFilters[filter.field] || {};
                      updateFilter(filter.field, { ...current, max: val });
                    }}
                  />
                </div>
              )}

              {filter.type === 'rating' && (
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => {
                    const current = localFilters[filter.field] || 0;
                    const active = star <= current;
                    return (
                      <button
                        key={star}
                        onClick={() => updateFilter(filter.field, star === current ? undefined : star)}
                        className="p-0.5"
                      >
                        <Star
                          className={`w-5 h-5 ${active ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                        />
                      </button>
                    );
                  })}
                </div>
              )}

              {filter.type === 'boolean' && (
                <label className="flex items-center gap-2 cursor-pointer">
                  <div
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      localFilters[filter.field] ? 'bg-blue-500' : 'bg-gray-200'
                    }`}
                    onClick={() => updateFilter(filter.field, !localFilters[filter.field])}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        localFilters[filter.field] ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {localFilters[filter.field] ? '是' : '否'}
                  </span>
                </label>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
