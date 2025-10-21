import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../../api/client'
import useAuthStore from '../../store/authStore'

export default function Login() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authAPI.login(formData)
      const { access_token, user } = response.data

      setAuth(user, access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: '500px', paddingTop: '4rem' }}>
      <div className="card">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            EchoForge
          </h1>
          <p className="text-muted">Your voice, your device.</p>
        </div>

        <h2>Sign In</h2>

        {error && (
          <div className="status-message status-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <span className="text-muted">Don't have an account? </span>
          <Link to="/register" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
