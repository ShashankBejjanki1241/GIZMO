/**
 * Gizmo AI - Main Application Page
 * Real-time task orchestration and monitoring interface
 * 
 * Developer: Shashank B
 * Repository: https://github.com/ShashankBejjanki1241/GIZMO
 * Last Updated: December 2024
 */

import React, { useState, useEffect, useRef } from 'react';
import { TaskEvent, Task, SystemHealth } from '../types';

export default function Home() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [taskEvents, setTaskEvents] = useState<TaskEvent[]>([]);
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [isReplaying, setIsReplaying] = useState(false);
  const [replaySpeed, setReplaySpeed] = useState(1);
  const replayIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [newTaskForm, setNewTaskForm] = useState({
    task_id: '',
    template: 'react',
    instruction: ''
  });

  // Pre-baked showcase tasks for public demo
  const showcaseTasks = [
    {
      id: "showcase-react-division",
      title: "React: Add Division Function",
      template: "react",
      instruction: "Add a division function to the calculator with proper divide-by-zero error handling and comprehensive tests",
      difficulty: "Easy"
    },
    {
      id: "showcase-express-health",
      title: "Express: Add Health Endpoint",
      template: "express", 
      instruction: "Implement a /health endpoint that returns server status, uptime, and basic system information with proper error handling",
      difficulty: "Easy"
    },
    {
      id: "showcase-flask-sum",
      title: "Flask: Add Sum Endpoint",
      template: "flask",
      instruction: "Create a /sum endpoint that accepts a list of numbers via POST and returns their sum with input validation and error handling",
      difficulty: "Easy"
    }
  ];

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runShowcase = async (showcaseTask: typeof showcaseTasks[0]) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Create the showcase task
      const response = await fetch('http://localhost:8003/api/v1/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: showcaseTask.id,
          template: showcaseTask.template,
          instruction: showcaseTask.instruction
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create showcase task: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Add to active tasks
      setTasks(prev => [...prev, {
        task_id: showcaseTask.id,
        run_id: result.run_id,
        template: showcaseTask.template,
        instruction: showcaseTask.instruction,
        state: 'starting',
        start_time: Date.now() / 1000,
        iteration: 0,
        current_agent: null,
        error: null
      }]);

      // Clear previous events for this task
      setTaskEvents([]);
      
      // Auto-select the new task
      setSelectedTask({
        task_id: showcaseTask.id,
        run_id: result.run_id,
        template: showcaseTask.template,
        instruction: showcaseTask.instruction,
        state: 'starting',
        start_time: Date.now() / 1000,
        iteration: 0,
        current_agent: null,
        error: null
      });
      fetchTaskEvents(showcaseTask.id);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start showcase task');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch system health
  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('http://localhost:8002/healthz');
      if (response.ok) {
        const health = await response.json();
        setSystemHealth(health);
      }
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/v1/tasks');
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      }
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  // Fetch task events
  const fetchTaskEvents = async (taskId: string) => {
    try {
      const response = await fetch(`http://localhost:8003/api/v1/tasks/${taskId}`);
      if (response.ok) {
        const data = await response.json();
        setTaskEvents(data.events || []);
      }
    } catch (error) {
      console.error('Failed to fetch task events:', error);
    }
  };

  // Create new task
  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8003/api/v1/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTaskForm),
      });

      if (response.ok) {
        const result = await response.json();
        setNewTaskForm({ task_id: '', template: 'react', instruction: '' });
        fetchTasks();
      }
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8003/ws');
    
    ws.onopen = () => {
      setWsStatus('connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'task_event') {
          setTaskEvents(prev => [...prev, data.event]);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      setWsStatus('disconnected');
    };
    
    return () => {
      ws.close();
    };
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchSystemHealth();
    fetchTasks();
    
    const interval = setInterval(() => {
      fetchSystemHealth();
      fetchTasks();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  // Replay functionality
  const startReplay = () => {
    if (taskEvents.length === 0) return;
    
    setIsReplaying(true);
    setTaskEvents([]);
    
    let currentIndex = 0;
    const replayEvents = taskEvents.slice();
    
    replayIntervalRef.current = setInterval(() => {
      if (currentIndex < replayEvents.length) {
        setTaskEvents(prev => [...prev, replayEvents[currentIndex]]);
        currentIndex++;
      } else {
        stopReplay();
      }
    }, 1000 / replaySpeed);
  };
  
  const stopReplay = () => {
    if (replayIntervalRef.current) {
      clearInterval(replayIntervalRef.current);
      replayIntervalRef.current = null;
    }
    setIsReplaying(false);
  };

  // Download functions
  const downloadPatch = (taskId: string, iteration: number) => {
    const event = taskEvents.find(e => e.iteration === iteration && e.stage === 'diff_applied');
    if (event?.data?.diff) {
      const blob = new Blob([event.data.diff], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${taskId}-patch-${iteration}.diff`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };
  
  const downloadLogs = (taskId: string, iteration: number) => {
    const event = taskEvents.find(e => e.iteration === iteration);
    if (event) {
      const logData = JSON.stringify(event, null, 2);
      const blob = new Blob([logData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${taskId}-logs-${iteration}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // Helper functions
  const getStageColor = (stage: string) => {
    const colors: { [key: string]: string } = {
      starting: 'bg-gray-100 text-gray-800',
      planning: 'bg-blue-100 text-blue-800',
      coding: 'bg-green-100 text-green-800',
      diff_applied: 'bg-purple-100 text-purple-800',
      testing: 'bg-yellow-100 text-yellow-800',
      test_report: 'bg-indigo-100 text-indigo-800',
      done: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  const getAgentIcon = (agent: string) => {
    const icons: { [key: string]: string } = {
      planner: '📋',
      coder: '💻',
      tester: '🧪'
    };
    return icons[agent] || '🤖';
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🚀 Gizmo AI</h1>
          <p className="text-xl text-gray-600">Multi-Agent AI Developer Platform</p>
          <p className="text-sm text-gray-500 mt-2">Watch AI agents plan, code, and test in real-time</p>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">System Health</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${systemHealth?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">{systemHealth?.status || 'Unknown'}</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">WebSocket Status</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${wsStatus === 'connected' ? 'bg-green-500' : wsStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600 capitalize">{wsStatus}</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Active Tasks</h3>
            <span className="text-2xl font-bold text-blue-600">{tasks.length}</span>
          </div>
        </div>

        {/* Showcase Section */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            🎯 Showcase Tasks
            <span className="ml-2 text-sm font-normal text-gray-600">(Click to run instantly)</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {showcaseTasks.map((task) => (
              <div key={task.id} className="bg-white rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition-colors">
                <h3 className="font-medium text-gray-800 mb-2">{task.title}</h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{task.instruction}</p>
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {task.difficulty}
                  </span>
                  <button
                    onClick={() => runShowcase(task)}
                    disabled={isLoading}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Starting...
                      </>
                    ) : (
                      <>
                        🚀 Run Showcase
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-500 mt-3 text-center">
            These pre-configured tasks demonstrate Gizmo AI's capabilities with real examples
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Task Management */}
          <div className="lg:col-span-1 space-y-6">
            {/* Create New Task */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
              <form onSubmit={createTask} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Task ID</label>
                  <input
                    type="text"
                    value={newTaskForm.task_id}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, task_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., add-division-function"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Template</label>
                  <select
                    value={newTaskForm.template}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, template: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="react">React + Jest</option>
                    <option value="express">Express + Supertest</option>
                    <option value="flask">Flask + pytest</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Instruction</label>
                  <textarea
                    value={newTaskForm.instruction}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, instruction: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Describe what you want the AI to implement..."
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  🚀 Start AI Task
                </button>
              </form>
            </div>

            {/* Active Tasks */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Tasks</h2>
              <div className="space-y-3">
                {tasks.map((task) => (
                  <div
                    key={task.task_id}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedTask?.task_id === task.task_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      setSelectedTask(task);
                      fetchTaskEvents(task.task_id);
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{task.task_id}</span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStageColor(task.state)}`}>
                        {task.state}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{task.instruction}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Iteration: {task.iteration}</span>
                      <span>{task.current_agent ? getAgentIcon(task.current_agent) : '⏳'}</span>
                    </div>
                  </div>
                ))}
                {tasks.length === 0 && (
                  <p className="text-gray-500 text-center py-4">No active tasks</p>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Task Details */}
          <div className="lg:col-span-2">
            {selectedTask ? (
              <div className="space-y-6">
                {/* Task Header */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{selectedTask.task_id}</h2>
                      <p className="text-gray-600 mt-1">{selectedTask.instruction}</p>
                    </div>
                    <div className="text-right">
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStageColor(selectedTask.state)}`}>
                        {selectedTask.state}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">Iteration {selectedTask.iteration}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Template:</span>
                      <p className="font-medium">{selectedTask.template}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Current Agent:</span>
                      <p className="font-medium">{selectedTask.current_agent || 'None'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Start Time:</span>
                      <p className="font-medium">{formatTimestamp(selectedTask.start_time)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Run ID:</span>
                      <p className="font-medium text-xs">{selectedTask.run_id}</p>
                    </div>
                  </div>
                </div>

                {/* Replay Controls */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Replay Controls</h3>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <label className="text-sm text-gray-700">Speed:</label>
                        <select
                          value={replaySpeed}
                          onChange={(e) => setReplaySpeed(Number(e.target.value))}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          <option value={0.5}>0.5x</option>
                          <option value={1}>1x</option>
                          <option value={2}>2x</option>
                          <option value={5}>5x</option>
                        </select>
                      </div>
                      
                      {!isReplaying ? (
                        <button
                          onClick={startReplay}
                          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                        >
                          ▶️ Start Replay
                        </button>
                      ) : (
                        <button
                          onClick={stopReplay}
                          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
                        >
                          ⏹️ Stop Replay
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Agent Timeline */}
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Timeline</h3>
                  <div className="space-y-4">
                    {taskEvents.map((event, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{getAgentIcon(event.stage === 'planning' ? 'planner' : event.stage === 'coding' ? 'coder' : 'tester')}</span>
                            <div>
                              <div className="font-medium text-gray-900">{event.stage}</div>
                              <div className="text-sm text-gray-500">Iteration {event.iteration}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-500">{formatTimestamp(event.timestamp)}</div>
                            <div className="flex space-x-2 mt-1">
                              {event.stage === 'diff_applied' && (
                                <button
                                  onClick={() => downloadPatch(selectedTask.task_id, event.iteration)}
                                  className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200"
                                >
                                  📥 Patch
                                </button>
                              )}
                              <button
                                onClick={() => downloadLogs(selectedTask.task_id, event.iteration)}
                                className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded hover:bg-gray-200"
                              >
                                📥 Logs
                              </button>
                            </div>
                          </div>
                        </div>
                        
                        <div className="text-sm text-gray-700 mb-2">{event.message}</div>
                        
                        {/* Event Data Display */}
                        {event.data && (
                          <div className="bg-gray-50 rounded p-3 text-sm">
                            {event.stage === 'planning' && event.data.plan && (
                              <div>
                                <div className="font-medium mb-2">Generated Plan:</div>
                                <ul className="list-disc list-inside space-y-1">
                                  {event.data.plan.plan?.map((step: string, i: number) => (
                                    <li key={i} className="text-gray-700">{step}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            
                            {event.stage === 'coding' && event.data.diff && (
                              <div>
                                <div className="font-medium mb-2">Generated Diff:</div>
                                <pre className="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto">
                                  {event.data.diff}
                                </pre>
                              </div>
                            )}
                            
                            {event.stage === 'diff_applied' && event.data.patch_result && (
                              <div>
                                <div className="font-medium mb-2">Patch Applied:</div>
                                <div className="grid grid-cols-2 gap-4 text-xs">
                                  <div>
                                    <span className="text-gray-500">Files Modified:</span>
                                    <p className="font-medium">{event.data.patch_result.applied_files?.length || 0}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Net Change:</span>
                                    <p className="font-medium">{event.data.patch_result.diff_stats?.net_change || 0} lines</p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {event.stage === 'testing' && event.data.test_results && (
                              <div>
                                <div className="font-medium mb-2">Test Results:</div>
                                <div className="grid grid-cols-3 gap-4 text-xs">
                                  <div>
                                    <span className="text-gray-500">Passed:</span>
                                    <p className="font-medium text-green-600">{event.data.test_results.test_summary?.passed || 0}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Failed:</span>
                                    <p className="font-medium text-red-600">{event.data.test_results.test_summary?.failed || 0}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Total:</span>
                                    <p className="font-medium">{event.data.test_results.test_summary?.total || 0}</p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {event.stage === 'test_report' && event.data.test_report && (
                              <div>
                                <div className="font-medium mb-2">Test Report:</div>
                                <div className="space-y-2">
                                  <div>
                                    <span className="text-gray-500">Summary:</span>
                                    <p className="font-medium">{event.data.test_report.test_summary}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Status:</span>
                                    <span className={`ml-2 px-2 py-1 rounded text-xs ${event.data.test_report.status === 'passed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                      {event.data.test_report.status}
                                    </span>
                                  </div>
                                  {event.data.test_report.recommendations && (
                                    <div>
                                      <span className="text-gray-500">Recommendations:</span>
                                      <ul className="list-disc list-inside mt-1">
                                        {event.data.test_report.recommendations.map((rec: string, i: number) => (
                                          <li key={i} className="text-gray-700">{rec}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {taskEvents.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No events yet. Task is starting...</p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                <div className="text-6xl mb-4">🤖</div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">Select a Task</h3>
                <p className="text-gray-500">Choose a task from the left panel to view its real-time progress</p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-gray-50 border-t mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              <span>Built with ❤️ by </span>
              <a 
                href="https://github.com/ShashankBejjanki1241" 
                target="_blank" 
                rel="noopener noreferrer"
                className="font-medium text-gray-700 hover:text-gray-900"
              >
                Shashank B
              </a>
            </div>
            <div className="text-sm text-gray-500">
              <a 
                href="https://github.com/ShashankBejjanki1241/GIZMO" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-gray-700"
              >
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
