import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../../api/client'
import useAuthStore from '../../store/authStore'

export default function Register() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
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
      // Register user
      await authAPI.register(formData)

      // Auto-login after registration
      const loginResponse = await authAPI.login({
        email: formData.email,
        password: formData.password,
      })

      const { access_token, user } = loginResponse.data
      setAuth(user, access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
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

        <h2>Create Account</h2>

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
            <label className="form-label">Username</label>
            <input
              type="text"
              name="username"
              className="form-input"
              value={formData.username}
              onChange={handleChange}
              required
              minLength={3}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Full Name (optional)</label>
            <input
              type="text"
              name="full_name"
              className="form-input"
              value={formData.full_name}
              onChange={handleChange}
              autoComplete="name"
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
              minLength={8}
              autoComplete="new-password"
            />
            <small className="text-muted">Minimum 8 characters</small>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <span className="text-muted">Already have an account? </span>
          <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
