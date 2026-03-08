import {
  MessageSquare,
  Rocket,
  Zap,
  Video,
  Search,
  Settings as SettingsIcon,
  LogoSvg
} from 'lucide-react'

type Tab = 'chat' | 'deployment' | 'agents' | 'video' | 'research' | 'settings'

interface SidebarProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
  isConnected: boolean
}

const tabs = [
  { id: 'chat' as Tab, label: 'Chat', icon: MessageSquare },
  { id: 'deployment' as Tab, label: 'Deployments', icon: Rocket },
  { id: 'agents' as Tab, label: 'Agents', icon: Zap },
  { id: 'video' as Tab, label: 'Video Gen', icon: Video },
  { id: 'research' as Tab, label: 'Research', icon: Search },
  { id: 'settings' as Tab, label: 'Settings', icon: SettingsIcon },
]

export function Sidebar({ activeTab, onTabChange, isConnected }: SidebarProps) {
  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded" />
          <div>
            <h1 className="font-bold text-lg">ArchonX</h1>
            <p className="text-xs text-gray-400">Agent OS</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-6 space-y-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-700 hover:text-gray-100'
            }`}
          >
            <Icon size={20} />
            <span className="font-medium">{label}</span>
          </button>
        ))}
      </nav>

      {/* Status */}
      <div className="px-6 py-4 border-t border-gray-700 space-y-3">
        <div className="text-xs text-gray-500">
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span>{isConnected ? 'Backend: Online' : 'Backend: Offline'}</span>
          </div>
          <p className="text-gray-600">v0.1.0</p>
        </div>
      </div>
    </div>
  )
}
