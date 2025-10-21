import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'

export default function Header() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/clone', label: 'Clone Voice' },
    { path: '/synthesize', label: 'Synthesize' },
    { path: '/library', label: 'Voice Library' },
  ]

  return (
    <header style={{
      background: 'var(--bg-card)',
      borderBottom: '1px solid var(--border)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem'
      }}>
        <Link to="/dashboard" style={{ textDecoration: 'none' }}>
          <h1 style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0
          }}>
            EchoForge
          </h1>
        </Link>

        <nav style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                textDecoration: 'none',
                color: location.pathname === item.path ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: location.pathname === item.path ? 600 : 500,
                transition: 'color 0.2s',
              }}
            >
              {item.label}
            </Link>
          ))}

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            marginLeft: '1rem',
            paddingLeft: '1rem',
            borderLeft: '1px solid var(--border)'
          }}>
            <span className="text-muted" style={{ fontSize: '0.9rem' }}>
              {user?.username}
            </span>
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
              Logout
            </button>
          </div>
        </nav>
      </div>
    </header>
  )
}
