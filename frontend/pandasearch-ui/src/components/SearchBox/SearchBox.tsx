import { useState, useCallback, useRef, useEffect } from 'react';
import { Search } from 'lucide-react';
import { suggest } from '../../services/api';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}

export function SearchBox({ onSearch, loading, placeholder = '🐼 胖达帮你搜索...' }: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Array<{ type: string; text: string; highlight?: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const wrapperRef = useRef<HTMLFormElement>(null);

  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q.trim()) {
      setSuggestions([]);
      return;
    }
    try {
      const data = await suggest(q.trim(), 8);
      setSuggestions(data.suggestions || []);
      setActiveIndex(-1);
    } catch (err) {
      console.error('Suggest error:', err);
      setSuggestions([]);
    }
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setQuery(value);
      setShowSuggestions(true);

      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      debounceRef.current = setTimeout(() => {
        fetchSuggestions(value);
      }, 300);
    },
    [fetchSuggestions]
  );

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      e?.preventDefault();
      if (debounceRef.current) clearTimeout(debounceRef.current);
      setShowSuggestions(false);
      if (query.trim()) {
        onSearch(query.trim());
      }
    },
    [query, onSearch]
  );

  const handleSuggestionClick = useCallback(
    (text: string) => {
      setQuery(text);
      setShowSuggestions(false);
      onSearch(text);
      inputRef.current?.focus();
    },
    [onSearch]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!showSuggestions || suggestions.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveIndex((prev) => (prev + 1) % suggestions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveIndex((prev) => (prev - 1 + suggestions.length) % suggestions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < suggestions.length) {
          handleSuggestionClick(suggestions[activeIndex].text);
        } else {
          handleSubmit();
        }
      } else if (e.key === 'Escape') {
        setShowSuggestions(false);
      }
    },
    [showSuggestions, suggestions, activeIndex, handleSuggestionClick, handleSubmit]
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <form ref={wrapperRef} onSubmit={handleSubmit} className="relative">
      <div className="flex items-center bg-white rounded-xl shadow-lg border border-gray-200 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
        <Search className="w-5 h-5 text-gray-400 ml-4" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim() && setShowSuggestions(true)}
          placeholder={placeholder}
          className="flex-1 px-4 py-3 text-gray-700 bg-transparent outline-none rounded-xl"
          disabled={loading}
          autoComplete="off"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mr-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '🐼 搜索中...' : '搜索'}
        </button>
      </div>

      {/* Autocomplete dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          <ul className="py-2">
            {suggestions.map((s, idx) => (
              <li
                key={idx}
                className={`px-4 py-2.5 cursor-pointer text-sm flex items-center gap-2 ${
                  idx === activeIndex ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                }`}
                onMouseEnter={() => setActiveIndex(idx)}
                onClick={() => handleSuggestionClick(s.text)}
              >
                <Search className="w-3.5 h-3.5 text-gray-400" />
                {s.highlight ? (
                  <span dangerouslySetInnerHTML={{ __html: s.highlight }} />
                ) : (
                  <span>{s.text}</span>
                )}
                {s.type && (
                  <span className="ml-auto text-xs text-gray-400 capitalize">{s.type}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}
