export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">CLI-Mate Dashboard</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          AI-Powered Error Analysis and Knowledge Base
        </p>
        <div className="mt-8 p-6 border rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Install the CLI tool: <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">pip install -e ./cli</code></li>
            <li>Run a command with wtf: <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">wtf python your_script.py</code></li>
            <li>View error analysis results here in the dashboard</li>
          </ol>
        </div>
      </div>
    </main>
  )
}
