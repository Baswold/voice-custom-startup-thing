import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './store/authStore'
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import Dashboard from './components/Dashboard/Dashboard'
import VoiceClone from './components/VoiceClone/VoiceClone'
import Synthesize from './components/Synthesize/Synthesize'
import VoiceLibrary from './components/VoiceLibrary/VoiceLibrary'
import Header from './components/Layout/Header'

function App() {
  const { user } = useAuthStore()

  return (
    <Router>
      <div className="app">
        {user && <Header />}
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/dashboard" /> : <Login />}
          />
          <Route
            path="/register"
            element={user ? <Navigate to="/dashboard" /> : <Register />}
          />
          <Route
            path="/dashboard"
            element={user ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/clone"
            element={user ? <VoiceClone /> : <Navigate to="/login" />}
          />
          <Route
            path="/synthesize"
            element={user ? <Synthesize /> : <Navigate to="/login" />}
          />
          <Route
            path="/library"
            element={user ? <VoiceLibrary /> : <Navigate to="/login" />}
          />
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
