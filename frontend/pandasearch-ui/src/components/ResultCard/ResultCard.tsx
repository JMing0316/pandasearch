import { SearchResultItem, SearchConfig } from '../../types/search';

interface ResultCardProps {
  item: SearchResultItem;
  config?: SearchConfig;
}

export function ResultCard({ item, config }: ResultCardProps) {
  const fieldsOrder: string[] = config?.presentation?.fields_order || Object.keys(item).filter(
    (k) => !['id', 'score', 'highlights'].includes(k)
  );
  const cardLayout = config?.presentation?.card_layout?.image_position || 'top';
  const isHorizontal = cardLayout === 'left';

  const inferType = (value: any): string => {
    if (typeof value === 'number') return 'number';
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))) {
      if (/\.(jpg|jpeg|png|gif|webp|svg)(\?.*)?$/i.test(value)) return 'image_url';
    }
    return 'text';
  };

  const renderField = (field: string) => {
    const value = item[field];
    const fieldConfig = config?.fields?.[field] || {};
    const fieldType = fieldConfig.type || inferType(value);
    const highlight = item.highlights?.[field];

    if (value == null) return null;

    // Image
    if (fieldType === 'image_url' || field === 'image_url' || field === 'image') {
      return (
        <img
          src={String(value)}
          alt={String(item.title || item.name || '')}
          className="w-full h-48 object-cover rounded-lg"
          loading="lazy"
        />
      );
    }

    // Currency / price
    if (fieldType === 'number' && fieldConfig.formatter === 'currency') {
      const num = typeof value === 'number' ? value : parseFloat(value);
      const formatted = isNaN(num) ? value : `¥${num.toFixed(2)}`;
      return (
        <span className="text-lg font-bold text-red-500">
          {formatted}
        </span>
      );
    }

    // Highlighted text
    if (highlight) {
      return (
        <span
          className="text-gray-700"
          dangerouslySetInnerHTML={{ __html: highlight }}
        />
      );
    }

    // Default text
    if (typeof value === 'string' || typeof value === 'number') {
      return <span className="text-gray-700">{String(value)}</span>;
    }

    return <span className="text-gray-700">{JSON.stringify(value)}</span>;
  };

  return (
    <div className={`bg-white rounded-xl shadow border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow ${isHorizontal ? 'flex gap-4' : ''}`}>
      {fieldsOrder.map((field) => {
        const fieldConfig = config?.fields?.[field] || {};
        const label = fieldConfig.label || field;
        const isImage = fieldConfig.type === 'image_url' || field === 'image_url' || field === 'image';

        return (
          <div
            key={field}
            className={`p-4 ${isImage && !isHorizontal ? 'p-0' : ''} ${isHorizontal && isImage ? 'w-48 flex-shrink-0 p-0' : ''}`}
          >
            {!isImage && (
              <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                {label}
              </div>
            )}
            <div className={isImage ? '' : 'text-sm'}>
              {renderField(field)}
            </div>
          </div>
        );
      })}

      {/* Relevance score */}
      <div className="px-4 pb-3 pt-0 flex items-center justify-end">
        <span className="text-xs text-gray-400">
          相关度: {(item.score * 100).toFixed(1)}%
        </span>
      </div>
    </div>
  );
}
