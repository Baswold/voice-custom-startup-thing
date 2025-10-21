import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { voiceAPI, jobAPI } from '../../api/client'
import useAuthStore from '../../store/authStore'

export default function Dashboard() {
  const { user } = useAuthStore()
  const [voices, setVoices] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [voicesRes, jobsRes] = await Promise.all([
        voiceAPI.listVoices(),
        jobAPI.listJobs(10)
      ])

      setVoices(voicesRes.data)
      setJobs(jobsRes.data)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      processing: 'badge-warning',
      completed: 'badge-success',
      failed: 'badge-danger'
    }
    return badges[status] || 'badge-warning'
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Welcome back, {user?.username || 'User'}!</h1>
        <p>Manage your voice profiles and create stunning AI voices</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '2.5rem', color: 'var(--primary)', marginBottom: '0.5rem' }}>
            {voices.length}
          </h3>
          <p className="text-muted">Voice Profiles</p>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '2.5rem', color: 'var(--success)', marginBottom: '0.5rem' }}>
            {jobs.filter(j => j.status === 'completed').length}
          </h3>
          <p className="text-muted">Completed Jobs</p>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '2.5rem', color: 'var(--secondary)', marginBottom: '0.5rem' }}>
            {user?.tier || 'Free'}
          </h3>
          <p className="text-muted">Account Tier</p>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2>Your Voice Profiles</h2>
          <Link to="/clone" className="btn btn-primary">
            + Clone New Voice
          </Link>
        </div>

        {voices.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p className="text-muted" style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
              You haven't cloned any voices yet
            </p>
            <Link to="/clone" className="btn btn-primary">
              Get Started
            </Link>
          </div>
        ) : (
          <div className="voice-grid">
            {voices.map((voice) => (
              <div key={voice.id} className="voice-card">
                <div className="voice-card-header">
                  <h3>{voice.name}</h3>
                  <span className={`badge ${voice.consent_verified ? 'badge-success' : 'badge-warning'}`}>
                    {voice.consent_verified ? 'Verified' : 'Pending'}
                  </span>
                </div>

                <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                  {voice.description || 'No description'}
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <span>{voice.duration_seconds.toFixed(1)}s</span>
                  <span>{voice.language.toUpperCase()}</span>
                </div>

                <Link
                  to={`/synthesize?voice=${voice.id}`}
                  className="btn btn-primary"
                  style={{ width: '100%', marginTop: '1rem' }}
                >
                  Use This Voice
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h2>Recent Jobs</h2>

        {jobs.length === 0 ? (
          <p className="text-muted" style={{ textAlign: 'center', padding: '2rem' }}>
            No jobs yet
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)', textAlign: 'left' }}>
                  <th style={{ padding: '1rem' }}>Job Type</th>
                  <th style={{ padding: '1rem' }}>Status</th>
                  <th style={{ padding: '1rem' }}>Progress</th>
                  <th style={{ padding: '1rem' }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '1rem' }}>{job.job_type}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`badge ${getStatusBadge(job.status)}`}>
                        {job.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${job.progress_percent}%` }}></div>
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }} className="text-muted">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
