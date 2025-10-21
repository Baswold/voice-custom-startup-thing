import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { voiceAPI, synthesisAPI, jobAPI } from '../../api/client'

export default function Synthesize() {
  const [searchParams] = useSearchParams()
  const preselectedVoiceId = searchParams.get('voice')

  const [voices, setVoices] = useState([])
  const [selectedVoice, setSelectedVoice] = useState(null)
  const [text, setText] = useState('')
  const [language, setLanguage] = useState('en')
  const [speed, setSpeed] = useState(1.0)

  const [synthesizing, setSynthesizing] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadVoices()
  }, [])

  useEffect(() => {
    if (preselectedVoiceId && voices.length > 0) {
      const voice = voices.find(v => v.id === parseInt(preselectedVoiceId))
      if (voice) {
        setSelectedVoice(voice)
        setLanguage(voice.language)
      }
    }
  }, [preselectedVoiceId, voices])

  useEffect(() => {
    if (jobId && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed') {
      const interval = setInterval(() => {
        checkJobStatus()
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [jobId, jobStatus])

  const loadVoices = async () => {
    try {
      const response = await voiceAPI.listVoices()
      const verifiedVoices = response.data.filter(v => v.consent_verified)
      setVoices(verifiedVoices)

      if (verifiedVoices.length > 0 && !selectedVoice) {
        setSelectedVoice(verifiedVoices[0])
        setLanguage(verifiedVoices[0].language)
      }
    } catch (err) {
      console.error('Failed to load voices:', err)
    }
  }

  const checkJobStatus = async () => {
    if (!jobId) return

    try {
      const response = await jobAPI.getJob(jobId)
      setJobStatus(response.data)

      if (response.data.status === 'completed') {
        setResult(response.data.output_data)
        setSynthesizing(false)
      } else if (response.data.status === 'failed') {
        setError(response.data.error_message || 'Synthesis failed')
        setSynthesizing(false)
      }
    } catch (err) {
      console.error('Failed to check job status:', err)
    }
  }

  const handleSynthesize = async () => {
    if (!selectedVoice) {
      setError('Please select a voice')
      return
    }

    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setSynthesizing(true)
    setError('')
    setResult(null)
    setJobStatus(null)

    try {
      const response = await synthesisAPI.synthesize({
        voice_profile_id: selectedVoice.id,
        text: text,
        language: language,
        speed: speed,
      })

      setJobId(response.data.job_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Synthesis failed')
      setSynthesizing(false)
    }
  }

  const exampleTexts = [
    "Welcome to EchoForge! This is a demonstration of AI voice cloning technology.",
    "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
    "Hello, my name is Alex. I'm excited to show you what this voice cloning platform can do.",
    "In a world where technology meets creativity, your voice becomes limitless.",
  ]

  if (voices.length === 0) {
    return (
      <div className="container">
        <div className="header">
          <h1>Synthesize Speech</h1>
          <p>Generate AI speech using your cloned voices</p>
        </div>

        <div className="card">
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <h2>No Voices Available</h2>
            <p className="text-muted" style={{ marginTop: '1rem', marginBottom: '2rem' }}>
              You need to clone a voice before you can synthesize speech.
            </p>
            <a href="/clone" className="btn btn-primary">
              Clone Your Voice
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Synthesize Speech</h1>
        <p>Generate AI speech using your cloned voices</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1.5rem' }}>
        {/* Voice Selector */}
        <div className="card">
          <h3>Select Voice</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            {voices.map((voice) => (
              <div
                key={voice.id}
                onClick={() => {
                  setSelectedVoice(voice)
                  setLanguage(voice.language)
                }}
                style={{
                  padding: '1rem',
                  border: `2px solid ${selectedVoice?.id === voice.id ? 'var(--primary)' : 'var(--border)'}`,
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  background: selectedVoice?.id === voice.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent'
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{voice.name}</div>
                <div className="text-muted" style={{ fontSize: '0.85rem' }}>
                  {voice.language.toUpperCase()} • {voice.duration_seconds.toFixed(1)}s
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Synthesis Panel */}
        <div className="card">
          <h2>Generate Speech</h2>

          {error && (
            <div className="status-message status-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Text to Synthesize</label>
            <textarea
              className="form-input form-textarea"
              placeholder="Enter the text you want to convert to speech..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
              maxLength={5000}
              disabled={synthesizing}
            />
            <small className="text-muted">{text.length} / 5000 characters</small>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            <small className="text-muted">Quick examples:</small>
            {exampleTexts.map((example, idx) => (
              <button
                key={idx}
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
                onClick={() => setText(example)}
                disabled={synthesizing}
              >
                Example {idx + 1}
              </button>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Language</label>
              <select
                className="form-input"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={synthesizing}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="zh">Chinese</option>
                <option value="ja">Japanese</option>
                <option value="ko">Korean</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Speed: {speed.toFixed(1)}x</label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={speed}
                onChange={(e) => setSpeed(parseFloat(e.target.value))}
                disabled={synthesizing}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSynthesize}
            disabled={synthesizing || !text.trim()}
            style={{ width: '100%' }}
          >
            {synthesizing ? '🎵 Generating...' : '🎵 Generate Speech'}
          </button>

          {/* Job Status */}
          {synthesizing && jobStatus && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className="status-message status-info">
                <strong>Status:</strong> {jobStatus.status}
                <div className="progress-bar" style={{ marginTop: '0.5rem' }}>
                  <div className="progress-fill" style={{ width: `${jobStatus.progress_percent}%` }}></div>
                </div>
              </div>
            </div>
          )}

          {/* Result */}
          {result && (
            <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '0.75rem', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <h3 style={{ color: 'var(--success)', marginBottom: '1rem' }}>✓ Speech Generated!</h3>

              <audio
                src={result.audio_url}
                controls
                style={{ width: '100%', marginBottom: '1rem' }}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
                <div>
                  <div className="text-muted">Duration</div>
                  <div style={{ fontWeight: 600 }}>{result.duration_seconds?.toFixed(2)}s</div>
                </div>
                <div>
                  <div className="text-muted">Language</div>
                  <div style={{ fontWeight: 600 }}>{result.language?.toUpperCase()}</div>
                </div>
              </div>

              <a
                href={result.audio_url}
                download="synthesis.wav"
                className="btn btn-success"
                style={{ width: '100%', marginTop: '1rem' }}
              >
                📥 Download Audio
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
