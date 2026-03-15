import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Chat } from './components/Chat'
import { DeploymentDash } from './components/DeploymentDash'
import { AgentMonitor } from './components/AgentMonitor'
import { VideoGenerator } from './components/VideoGenerator'
import { ResearchPanel } from './components/ResearchPanel'
import { Settings } from './components/Settings'
import { Sidebar } from './components/Sidebar'
import { invoke } from '@tauri-apps/api/tauri'

const queryClient = new QueryClient()

type Tab = 'chat' | 'deployment' | 'agents' | 'video' | 'research' | 'settings'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Check backend connectivity
    const checkConnection = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/health')
        setIsConnected(response.ok)
      } catch {
        setIsConnected(false)
      }
    }

    checkConnection()
    const interval = setInterval(checkConnection, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen bg-gray-900 text-gray-100">
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} isConnected={isConnected} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="border-b border-gray-700 bg-gray-800 px-6 py-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold">ArchonX OS Control Tower</h1>
            <div className="flex items-center gap-4">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </header>

          {/* Tab Content */}
          <div className="flex-1 overflow-auto">
            {activeTab === 'chat' && <Chat />}
            {activeTab === 'deployment' && <DeploymentDash />}
            {activeTab === 'agents' && <AgentMonitor />}
            {activeTab === 'video' && <VideoGenerator />}
            {activeTab === 'research' && <ResearchPanel />}
            {activeTab === 'settings' && <Settings />}
          </div>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App
