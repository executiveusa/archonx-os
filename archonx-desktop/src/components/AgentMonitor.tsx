import { useQuery } from '@tanstack/react-query'
import { Zap, RefreshCw } from 'lucide-react'

interface Agent {
  id: string
  name: string
  status: 'idle' | 'busy' | 'error'
  crew: string
  current_task?: string
}

export function AgentMonitor() {
  const { data: agents, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/agents')
      return res.json()
    },
    refetchInterval: 5000,
  })

  const crewStats = agents?.agents?.reduce(
    (acc: any, agent: Agent) => {
      if (!acc[agent.crew]) {
        acc[agent.crew] = { total: 0, busy: 0, idle: 0, error: 0 }
      }
      acc[agent.crew].total++
      acc[agent.crew][agent.status]++
      return acc
    },
    {}
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Zap size={24} />
          Agent Monitor
        </h2>
        <button
          onClick={() => refetch()}
          className="bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded flex items-center gap-2"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Crew Stats */}
      <div className="px-6 py-4 border-b border-gray-700 grid grid-cols-3 gap-4">
        {crewStats &&
          Object.entries(crewStats).map(([crew, stats]: any) => (
            <div key={crew} className="bg-gray-700 rounded p-3">
              <p className="text-sm text-gray-400 mb-2 font-medium">{crew} Crew</p>
              <div className="space-y-1 text-xs">
                <p>
                  <span className="text-gray-500">Total:</span>{' '}
                  <span className="text-white font-bold">{stats.total}</span>
                </p>
                <p>
                  <span className="text-green-400">Idle:</span> {stats.idle}
                </p>
                <p>
                  <span className="text-yellow-400">Busy:</span> {stats.busy}
                </p>
                <p>
                  <span className="text-red-400">Error:</span> {stats.error}
                </p>
              </div>
            </div>
          ))}
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-auto p-6">
        <div className="space-y-3">
          {agents?.agents?.map((agent: Agent) => (
            <div key={agent.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-bold">{agent.name}</h3>
                  <p className="text-xs text-gray-400">{agent.crew} Crew</p>
                </div>
                <div
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    agent.status === 'idle'
                      ? 'bg-green-900 text-green-200'
                      : agent.status === 'busy'
                        ? 'bg-yellow-900 text-yellow-200'
                        : 'bg-red-900 text-red-200'
                  }`}
                >
                  {agent.status}
                </div>
              </div>
              {agent.current_task && (
                <p className="text-sm text-gray-300">Current: {agent.current_task}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
