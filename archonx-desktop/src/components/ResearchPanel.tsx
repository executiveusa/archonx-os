import { useState } from 'react'
import { Search, Plus, Trash2 } from 'lucide-react'

interface ResearchItem {
  id: string
  query: string
  results: string[]
  timestamp: string
}

export function ResearchPanel() {
  const [query, setQuery] = useState('')
  const [research, setResearch] = useState<ResearchItem[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return

    setIsSearching(true)
    try {
      const res = await fetch('http://127.0.0.1:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })
      const data = await res.json()

      const item: ResearchItem = {
        id: Date.now().toString(),
        query,
        results: data.results || [],
        timestamp: new Date().toISOString(),
      }

      setResearch((prev) => [item, ...prev])
      setQuery('')
    } catch (error) {
      console.error('Research error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
          <Search size={24} />
          Research Tools
        </h2>

        {/* Search Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter research query..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus size={18} />
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {research.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No research results yet. Start by searching.</p>
          </div>
        ) : (
          research.map((item) => (
            <div
              key={item.id}
              className="bg-gray-700 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-bold">{item.query}</h3>
                <button
                  onClick={() =>
                    setResearch((prev) => prev.filter((r) => r.id !== item.id))
                  }
                  className="text-gray-400 hover:text-red-400 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <div className="space-y-2">
                {item.results.map((result, idx) => (
                  <p key={idx} className="text-sm text-gray-300">
                    • {result}
                  </p>
                ))}
              </div>

              <p className="text-xs text-gray-500 mt-3">
                {new Date(item.timestamp).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
