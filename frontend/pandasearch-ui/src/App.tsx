import { useState } from 'react'
import { SearchBox } from './components/SearchBox'
import { ResultList } from './components/ResultList'
import { FilterPanel } from './components/FilterPanel'
import { SortBar } from './components/SortBar'
import { AISummary } from './components/AISummary'

function App() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [aiSummary, setAiSummary] = useState('')

  const handleSearch = async (query: string) => {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      const data = await res.json()
      setResults(data.products || [])
      setAiSummary(data.ai_summary || '')
    } catch (err) {
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

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
            <FilterPanel />
          </aside>

          {/* Results */}
          <div className="flex-1">
            <SortBar />
            <ResultList results={results} loading={loading} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
