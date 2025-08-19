import { useState, useEffect } from 'react'
import Head from 'next/head'

interface TaskEvent {
  task_id: string
  run_id: string
  iteration: number
  stage: string
  timestamp: number
  data: any
  message: string
}

interface TaskRun {
  task_id: string
  run_id: string
  template: string
  instruction: string
  state: string
  iteration: number
  start_time: number
  events: TaskEvent[]
  current_agent?: string
  error?: string
}

export default function Home() {
  const [apiHealth, setApiHealth] = useState<any>(null)
  const [orchestratorHealth, setOrchestratorHealth] = useState<any>(null)
  const [tasks, setTasks] = useState<TaskRun[]>([])
  const [events, setEvents] = useState<TaskEvent[]>([])
  const [wsConnected, setWsConnected] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  
  // Task creation form state
  const [taskForm, setTaskForm] = useState({
    task_id: '',
    template: 'react' as 'react' | 'express' | 'flask',
    instruction: ''
  })

  useEffect(() => {
    // Check API health
    checkApiHealth()
    checkOrchestratorHealth()
    loadTasks()
    
    // Setup WebSocket connection
    setupWebSocket()
    
    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8002/healthz')
      const data = await response.json()
      setApiHealth(data)
    } catch (error) {
      setApiHealth({ error: 'API unreachable' })
    }
  }

  const checkOrchestratorHealth = async () => {
    try {
      const response = await fetch('http://localhost:8003/healthz')
      const data = await response.json()
      setOrchestratorHealth(data)
    } catch (error) {
      setOrchestratorHealth({ error: 'Orchestrator unreachable' })
    }
  }

  const loadTasks = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/v1/tasks')
      const data = await response.json()
      setTasks(data.tasks || [])
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }

  const setupWebSocket = () => {
    const websocket = new WebSocket('ws://localhost:8003/ws')
    
    websocket.onopen = () => {
      setWsConnected(true)
      console.log('WebSocket connected')
    }
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.task_id && data.stage) {
          // This is a task event
          setEvents(prev => [...prev, data])
        }
      } catch (error) {
        // Not JSON, probably connection message
        console.log('WebSocket message:', event.data)
      }
    }
    
    websocket.onclose = () => {
      setWsConnected(false)
      console.log('WebSocket disconnected')
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setWsConnected(false)
    }
    
    setWs(websocket)
  }

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!taskForm.task_id || !taskForm.instruction) {
      alert('Please fill in all fields')
      return
    }
    
    try {
      const response = await fetch('http://localhost:8003/api/v1/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskForm),
      })
      
      const result = await response.json()
      
      if (result.status === 'success') {
        alert('Task created successfully!')
        setTaskForm({ task_id: '', template: 'react', instruction: '' })
        loadTasks() // Reload tasks list
      } else {
        alert(`Failed to create task: ${result.message}`)
      }
    } catch (error) {
      console.error('Error creating task:', error)
      alert('Failed to create task')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'running': return 'text-blue-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'done': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'testing': return 'bg-yellow-100 text-yellow-800'
      case 'coding': return 'bg-blue-100 text-blue-800'
      case 'planning': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

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
              Transparent AI-assisted development system
            </p>
          </div>

          {/* System Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">API Status</h2>
              {apiHealth ? (
                <div className="space-y-2">
                  <p className={`font-medium ${getStatusColor(apiHealth.status)}`}>
                    Status: {apiHealth.status || 'Unknown'}
                  </p>
                  {apiHealth.uptime && (
                    <p className="text-sm text-gray-600">
                      Uptime: {Math.round(apiHealth.uptime / 60)} minutes
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">Checking...</p>
              )}
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Orchestrator Status</h2>
              {orchestratorHealth ? (
                <div className="space-y-2">
                  <p className={`font-medium ${getStatusColor(orchestratorHealth.status)}`}>
                    Status: {orchestratorHealth.status || 'Unknown'}
                  </p>
                  {orchestratorHealth.uptime && (
                    <p className="text-sm text-gray-600">
                      Uptime: {Math.round(orchestratorHealth.uptime / 60)} minutes
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">Checking...</p>
              )}
            </div>
          </div>

          {/* WebSocket Status */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold mb-4">Real-time Connection</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={wsConnected ? 'text-green-600' : 'text-red-600'}>
                {wsConnected ? 'WebSocket Connected' : 'WebSocket Disconnected'}
              </span>
            </div>
          </div>

          {/* Task Creation Form */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold mb-4">Create New Task</h2>
            <form onSubmit={createTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task ID
                </label>
                <input
                  type="text"
                  value={taskForm.task_id}
                  onChange={(e) => setTaskForm(prev => ({ ...prev, task_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter unique task ID"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template
                </label>
                <select
                  value={taskForm.template}
                  onChange={(e) => setTaskForm(prev => ({ ...prev, template: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="react">React + Jest</option>
                  <option value="express">Express + Supertest</option>
                  <option value="flask">Flask + pytest</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instruction
                </label>
                <textarea
                  value={taskForm.instruction}
                  onChange={(e) => setTaskForm(prev => ({ ...prev, instruction: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Describe what you want the AI to do..."
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Create Task
              </button>
            </form>
          </div>

          {/* Active Tasks */}
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold mb-4">Active Tasks</h2>
            {tasks.length === 0 ? (
              <p className="text-gray-500">No active tasks</p>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div key={task.task_id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium">{task.task_id}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStageColor(task.state)}`}>
                        {task.state}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{task.instruction}</p>
                    <div className="text-xs text-gray-500">
                      <span>Template: {task.template}</span>
                      <span className="mx-2">•</span>
                      <span>Iteration: {task.iteration}</span>
                      {task.current_agent && (
                        <>
                          <span className="mx-2">•</span>
                          <span>Agent: {task.current_agent}</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Real-time Events */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Real-time Events</h2>
            {events.length === 0 ? (
              <p className="text-gray-500">No events yet. Create a task to see events in real-time.</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {events.slice().reverse().map((event, index) => (
                  <div key={`${event.task_id}-${event.iteration}-${index}`} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-sm">{event.task_id}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStageColor(event.stage)}`}>
                        {event.stage}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{event.message}</p>
                    <div className="text-xs text-gray-500 mt-1">
                      <span>Run: {event.run_id.slice(-8)}</span>
                      <span className="mx-2">•</span>
                      <span>Iteration: {event.iteration}</span>
                      <span className="mx-2">•</span>
                      <span>{new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}
