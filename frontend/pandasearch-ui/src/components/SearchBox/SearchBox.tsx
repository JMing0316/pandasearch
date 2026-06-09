import { useState, useCallback } from 'react'
import { Search } from 'lucide-react'

interface SearchBoxProps {
  onSearch: (query: string) => void
  loading?: boolean
  placeholder?: string
}

export function SearchBox({ onSearch, loading, placeholder = '🐼 胖达帮你搜索...' }: SearchBoxProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }, [query, onSearch])

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center bg-white rounded-xl shadow-lg border border-gray-200 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
        <Search className="w-5 h-5 text-gray-400 ml-4" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="flex-1 px-4 py-3 text-gray-700 bg-transparent outline-none rounded-xl"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mr-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '🐼 搜索中...' : '搜索'}
        </button>
      </div>
    </form>
  )
}
