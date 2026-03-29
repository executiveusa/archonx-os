'use client'

export default function ErrorPage({ error }: { error: Error }) {
  return (
    <main className="flex items-center justify-center w-full h-screen bg-black text-white">
      <div className="text-center max-w-lg px-6">
        <h1 className="text-3xl font-bold mb-2">Chess Theater</h1>
        <p className="text-gray-400 mb-4">
          Something went wrong loading the 3D scene.
        </p>
        <p className="text-sm text-gray-600 font-mono">{error.message}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 px-4 py-2 bg-white text-black rounded font-medium hover:bg-gray-200 transition-colors"
        >
          Reload
        </button>
      </div>
    </main>
  )
}
