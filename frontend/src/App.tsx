import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { 
  Home, Users, CheckCircle, Plus, Trash2 
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

function App() {
  return (
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
  )
}

// ... остальной код остается таким же
