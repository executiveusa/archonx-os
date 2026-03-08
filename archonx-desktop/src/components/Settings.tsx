import { useState } from 'react'
import { Settings as SettingsIcon, Save } from 'lucide-react'

interface Config {
  coolify_api_key: string
  coolify_base_url: string
  openclaw_url: string
  n8n_url: string
  n8n_api_key: string
  claude_api_key: string
  default_model: string
}

export function Settings() {
  const [config, setConfig] = useState<Config>({
    coolify_api_key: '',
    coolify_base_url: '',
    openclaw_url: 'ws://127.0.0.1:18789',
    n8n_url: '',
    n8n_api_key: '',
    claude_api_key: '',
    default_model: 'claude-3-5-sonnet',
  })

  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    try {
      await fetch('http://127.0.0.1:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Settings error:', error)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <SettingsIcon size={24} />
          Settings
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl space-y-6">
          {/* Coolify */}
          <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
            <h3 className="font-bold mb-4">Coolify Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 block mb-2">API Key</label>
                <input
                  type="password"
                  value={config.coolify_api_key}
                  onChange={(e) =>
                    setConfig({ ...config, coolify_api_key: e.target.value })
                  }
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-2">Base URL</label>
                <input
                  type="text"
                  value={config.coolify_base_url}
                  onChange={(e) =>
                    setConfig({ ...config, coolify_base_url: e.target.value })
                  }
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* OpenClaw */}
          <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
            <h3 className="font-bold mb-4">OpenClaw Configuration</h3>
            <div>
              <label className="text-sm text-gray-400 block mb-2">WebSocket URL</label>
              <input
                type="text"
                value={config.openclaw_url}
                onChange={(e) =>
                  setConfig({ ...config, openclaw_url: e.target.value })
                }
                className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* n8n */}
          <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
            <h3 className="font-bold mb-4">n8n Workflows</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 block mb-2">Instance URL</label>
                <input
                  type="text"
                  value={config.n8n_url}
                  onChange={(e) => setConfig({ ...config, n8n_url: e.target.value })}
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-2">API Key</label>
                <input
                  type="password"
                  value={config.n8n_api_key}
                  onChange={(e) =>
                    setConfig({ ...config, n8n_api_key: e.target.value })
                  }
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Claude */}
          <div className="bg-gray-700 rounded-lg p-6 border border-gray-600">
            <h3 className="font-bold mb-4">Claude API</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 block mb-2">API Key</label>
                <input
                  type="password"
                  value={config.claude_api_key}
                  onChange={(e) =>
                    setConfig({ ...config, claude_api_key: e.target.value })
                  }
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-2">Default Model</label>
                <select
                  value={config.default_model}
                  onChange={(e) =>
                    setConfig({ ...config, default_model: e.target.value })
                  }
                  className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-100 focus:outline-none focus:border-blue-500"
                >
                  <option>claude-3-5-sonnet</option>
                  <option>claude-3-opus</option>
                  <option>claude-3-haiku</option>
                </select>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium flex items-center gap-2 justify-center transition-colors"
          >
            <Save size={18} />
            Save Configuration
          </button>

          {saved && (
            <div className="bg-green-900 border border-green-600 rounded px-4 py-3 text-green-200">
              ✓ Settings saved successfully
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
