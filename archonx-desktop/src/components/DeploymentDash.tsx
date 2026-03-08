import { useQuery } from '@tanstack/react-query'
import { Rocket, RefreshCw, AlertCircle } from 'lucide-react'

interface Service {
  uuid: string
  name: string
  status: string
  url?: string
  last_deploy?: string
}

export function DeploymentDash() {
  const { data: services, isLoading, refetch } = useQuery({
    queryKey: ['services'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/deployments')
      return res.json()
    },
    refetchInterval: 30000,
  })

  const handleDeploy = async (uuid: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/deployments/${uuid}/deploy`, {
        method: 'POST',
      })
      const data = await res.json()
      console.log('Deployment started:', data)
      refetch()
    } catch (error) {
      console.error('Deploy error:', error)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Rocket size={24} />
          Coolify Deployments
        </h2>
        <button
          onClick={() => refetch()}
          className="bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded flex items-center gap-2 transition-colors"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Services Grid */}
      <div className="flex-1 overflow-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400">Loading services...</p>
          </div>
        ) : !services?.services || services.services.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No services available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.services.map((service: Service) => (
              <div
                key={service.uuid}
                className="bg-gray-700 rounded-lg p-4 border border-gray-600 hover:border-blue-500 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-bold text-lg">{service.name}</h3>
                  <div
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      service.status === 'running'
                        ? 'bg-green-900 text-green-200'
                        : 'bg-yellow-900 text-yellow-200'
                    }`}
                  >
                    {service.status}
                  </div>
                </div>

                {service.url && (
                  <p className="text-sm text-gray-400 mb-3 truncate">{service.url}</p>
                )}

                {service.last_deploy && (
                  <p className="text-xs text-gray-500 mb-4">
                    Last deploy: {new Date(service.last_deploy).toLocaleDateString()}
                  </p>
                )}

                <button
                  onClick={() => handleDeploy(service.uuid)}
                  className="w-full bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-medium transition-colors"
                >
                  Deploy Now
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
