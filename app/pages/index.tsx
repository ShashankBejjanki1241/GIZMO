import { useState, useEffect } from 'react'
import Head from 'next/head'

export default function Home() {
  const [apiStatus, setApiStatus] = useState<string>('checking...')
  const [orchestratorStatus, setOrchestratorStatus] = useState<string>('checking...')

  useEffect(() => {
    // Check API health
    fetch('http://localhost:8002/healthz')
      .then(response => response.json())
      .then(data => {
        setApiStatus(data.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy')
      })
      .catch(() => {
        setApiStatus('❌ Not responding')
      })

    // Check orchestrator health
    fetch('http://localhost:8003/healthz')
      .then(response => response.json())
      .then(data => {
        setOrchestratorStatus(data.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy')
      })
      .catch(() => {
        setOrchestratorStatus('❌ Not responding')
      })
  }, [])

  return (
    <>
      <Head>
        <title>Gizmo AI</title>
        <meta name="description" content="Transparent AI-assisted development system" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Gizmo AI
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Transparent, safe, and demo-able system for end-to-end AI-assisted development
            </p>
            
            <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                System Status
              </h2>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">Frontend (Next.js)</span>
                  <span className="text-green-600 font-semibold">✅ Running</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">API (FastAPI)</span>
                  <span className="font-semibold">{apiStatus}</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">Orchestrator</span>
                  <span className="font-semibold">{orchestratorStatus}</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">Database (PostgreSQL)</span>
                  <span className="text-gray-500">Check with: make health</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">Cache (Redis)</span>
                  <span className="text-gray-500">Check with: make health</span>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Quick Commands</h3>
                <div className="text-sm text-blue-700 space-y-1">
                  <div><code className="bg-blue-100 px-2 py-1 rounded">make up</code> - Start all services</div>
                  <div><code className="bg-blue-100 px-2 py-1 rounded">make health</code> - Check service health</div>
                  <div><code className="bg-blue-100 px-2 py-1 rounded">make logs</code> - Monitor logs</div>
                  <div><code className="bg-blue-100 px-2 py-1 rounded">make down</code> - Stop all services</div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">Service URLs</h3>
                <div className="text-sm text-green-700 space-y-1">
                  <div><strong>Frontend:</strong> <a href="http://localhost:3002" className="underline">http://localhost:3002</a></div>
                  <div><strong>API:</strong> <a href="http://localhost:8002" className="underline">http://localhost:8002</a></div>
                  <div><strong>Orchestrator:</strong> <a href="http://localhost:8003" className="underline">http://localhost:8003</a></div>
                  <div><strong>Database:</strong> localhost:5433</div>
                  <div><strong>Redis:</strong> localhost:6380</div>
                </div>
              </div>
            </div>
            
            <div className="mt-8 text-sm text-gray-500">
              <p>Status: 🚧 In Development (MVP Phase)</p>
              <p>Check <code className="bg-gray-100 px-2 py-1 rounded">BACKLOG.md</code> for current scope</p>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
