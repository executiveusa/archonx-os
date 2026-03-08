import { useState } from 'react'
import { Video, Play, Download } from 'lucide-react'

export function VideoGenerator() {
  const [script, setScript] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!script.trim()) return

    setIsGenerating(true)
    try {
      const res = await fetch('http://127.0.0.1:8000/api/video/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script }),
      })
      const data = await res.json()
      setVideoUrl(data.video_url)
    } catch (error) {
      console.error('Video generation error:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Video size={24} />
          Video Generator (StoryToolkitAI)
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 grid grid-cols-2 gap-6">
        {/* Script Editor */}
        <div className="flex flex-col">
          <label className="text-sm font-medium mb-2">Video Script</label>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Write your video script here..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg p-4 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
          />
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !script.trim()}
            className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-lg font-medium flex items-center gap-2 justify-center transition-colors"
          >
            <Play size={18} />
            {isGenerating ? 'Generating...' : 'Generate Video'}
          </button>
        </div>

        {/* Preview */}
        <div className="flex flex-col">
          <label className="text-sm font-medium mb-2">Preview</label>
          {videoUrl ? (
            <div className="bg-gray-700 rounded-lg p-4 flex flex-col h-full">
              <video
                src={videoUrl}
                controls
                className="w-full flex-1 rounded bg-black"
              />
              <button className="mt-4 bg-green-600 hover:bg-green-700 px-4 py-2 rounded flex items-center gap-2 justify-center transition-colors">
                <Download size={18} />
                Download
              </button>
            </div>
          ) : (
            <div className="bg-gray-700 rounded-lg p-8 flex items-center justify-center h-full text-gray-400">
              Video preview will appear here
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
