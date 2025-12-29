import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { 
  Home, Users, UserPlus, CheckCircle, Plus, Edit, Trash2 
} from 'lucide-react'
import axios from 'axios'

const API_BASE = 'http://localhost:5000'

interface Todo {
  id: number
  user_id: number
  task: string
  completed: boolean
  created_at: string
}

interface User {
  id: number
  name: string
  email: string
  created_at: string
}

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600">
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/todos" element={<TodosPage />} />
            <Route path="/users" element={<UsersPage />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

function Navbar() {
  return (
    <nav className="bg-white/20 backdrop-blur-lg shadow-lg border-b border-white/20">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2 text-xl font-bold text-white">
            <CheckCircle className="w-8 h-8" />
            <span>TODO App</span>
          </Link>
          <div className="flex space-x-4">
            <Link to="/" className="flex items-center space-x-1 text-white hover:text-white/80 transition">
              <Home className="w-5 h-5" />
              <span>Главная</span>
            </Link>
            <Link to="/todos" className="flex items-center space-x-1 text-white hover:text-white/80 transition">
              <Plus className="w-5 h-5" />
              <span>Задачи</span>
            </Link>
            <Link to="/users" className="flex items-center space-x-1 text-white hover:text-white/80 transition">
              <Users className="w-5 h-5" />
              <span>Пользователи</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-20">
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-white mb-6">Добро пожаловать в TODO App</h1>
        <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Современное приложение для управления задачами с поддержкой пользователей.
          FastAPI + PostgreSQL + React + Docker.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            to="/todos" 
            className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold hover:bg-white/90 transition shadow-2xl"
          >
            Управление задачами
          </Link>
          <Link 
            to="/users" 
            className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold hover:bg-white/30 transition"
          >
            Управление пользователями
          </Link>
        </div>
      </div>
      
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h3 className="text-2xl font-bold text-white mb-4">🚀 Технологии</h3>
          <ul className="space-y-2 text-white/90">
            <li>FastAPI (Backend)</li>
            <li>PostgreSQL 18</li>
            <li>React 18 + TypeScript</li>
            <li>Tailwind CSS</li>
            <li>Docker Compose</li>
          </ul>
        </div>
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <h3 className="text-2xl font-bold text-white mb-4">📊 API Документация</h3>
          <a 
            href="http://localhost:5000/docs" 
            target="_blank"
            className="inline-flex items-center space-x-2 bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-600 transition"
          >
            Открыть Swagger UI
          </a>
        </div>
      </div>
    </div>
  )
}

function TodosPage() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [newTodo, setNewTodo] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTodo, setEditTodo] = useState('')

  useEffect(() => {
    fetchTodos()
  }, [])

  const fetchTodos = async () => {
    try {
      const response = await axios.get(`${API_BASE}/todos`)
      setTodos(response.data)
    } catch (error) {
      console.error('Ошибка загрузки задач:', error)
    }
  }

  const createTodo = async () => {
    if (!newTodo.trim()) return
    
    try {
      await axios.post(`${API_BASE}/todos`, {
        user_id: 1,
        task: newTodo,
        completed: false
      })
      setNewTodo('')
      fetchTodos()
    } catch (error) {
      console.error('Ошибка создания задачи:', error)
    }
  }

  const toggleTodo = async (id: number, completed: boolean) => {
    try {
      await axios.put(`${API_BASE}/todos/${id}`, {
        task: todos.find(t => t.id === id)?.task || '',
        completed: !completed
      })
      fetchTodos()
    } catch (error) {
      console.error('Ошибка обновления задачи:', error)
    }
  }

  const deleteTodo = async (id: number) => {
    if (!confirm('Удалить задачу?')) return
    
    try {
      await axios.delete(`${API_BASE}/todos/${id}`)
      fetchTodos()
    } catch (error) {
      console.error('Ошибка удаления задачи:', error)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">📝 Управление задачами</h1>
        <p className="text-xl text-white/90">Добавляйте, редактируйте и управляйте своими задачами</p>
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            placeholder="Новая задача..."
            className="flex-1 bg-white/20 border border-white/30 rounded-2xl px-6 py-4 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50"
            onKeyPress={(e) => e.key === 'Enter' && createTodo()}
          />
          <button
            onClick={createTodo}
            className="bg-green-500 hover:bg-green-600 text-white px-8 py-4 rounded-2xl font-semibold transition shadow-lg hover:shadow-xl"
          >
            Добавить
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {todos.map((todo) => (
          <div
            key={todo.id}
            className={`flex items-center justify-between p-6 rounded-2xl border border-white/20 bg-white/5 backdrop-blur-lg transition-all hover:bg-white/10 ${
              todo.completed ? 'opacity-60' : ''
            }`}
          >
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-2">
                <button
                  onClick={() => toggleTodo(todo.id, todo.completed)}
                  className={`w-6 h-6 rounded-full flex items-center justify-center border-2 transition-all ${
                    todo.completed
                      ? 'bg-green-500 border-green-500 text-white'
                      : 'border-white/50 hover:border-white'
                  }`}
                >
                  {todo.completed && '✓'}
                </button>
                <h3 className={`text-xl font-semibold text-white ${todo.completed ? 'line-through' : ''}`}>
                  {todo.task}
                </h3>
              </div>
              <p className="text-white/70 text-sm">ID: {todo.id} | Создано: {new Date(todo.created_at).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setEditingId(todo.id)
                  setEditTodo(todo.task)
                }}
                className="p-2 text-blue-400 hover:text-blue-300 transition"
                title="Редактировать"
              >
                <Edit className="w-5 h-5" />
              </button>
              <button
                onClick={() => deleteTodo(todo.id)}
                className="p-2 text-red-400 hover:text-red-300 transition"
                title="Удалить"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {todos.length === 0 && (
        <div className="text-center py-20">
          <CheckCircle className="w-24 h-24 text-white/50 mx-auto mb-4" />
          <h3 className="text-2xl font-semibold text-white/70 mb-2">Нет задач</h3>
          <p className="text-white/50 mb-8">Добавьте первую задачу выше</p>
        </div>
      )}
    </div>
  )
}

function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [newUser, setNewUser] = useState({ name: '', email: '' })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/users`)
      setUsers(response.data)
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error)
    }
  }

  const createUser = async () => {
    try {
      await axios.post(`${API_BASE}/users`, newUser)
      setNewUser({ name: '', email: '' })
      fetchUsers()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка создания пользователя')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">👥 Управление пользователями</h1>
        <p className="text-xl text-white/90">Добавляйте новых пользователей</p>
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            value={newUser.name}
            onChange={(e) => setNewUser({...newUser, name: e.target.value})}
            placeholder="Имя"
            className="bg-white/20 border border-white/30 rounded-2xl px-6 py-4 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50"
          />
          <input
            type="email"
            value={newUser.email}
            onChange={(e) => setNewUser({...newUser, email: e.target.value})}
            placeholder="email@example.com"
            className="bg-white/20 border border-white/30 rounded-2xl px-6 py-4 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50"
          />
          <button
            onClick={createUser}
            className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-2xl font-semibold transition shadow-lg hover:shadow-xl"
          >
            <UserPlus className="w-5 h-5 inline mr-2" />
            Создать
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {users.map((user) => (
          <div key={user.id} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-white">{user.name}</h3>
                <p className="text-white/70">{user.email}</p>
              </div>
              <div className="text-white/50 text-sm">
                ID: {user.id} | {new Date(user.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
