import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { voiceAPI } from '../../api/client'
import AudioRecorder from './AudioRecorder'

const TTS_MODELS = [
  {
    id: 'xtts_v2',
    name: 'XTTS v2',
    description: 'Multilingual, broadcast-quality voice cloning. Best overall quality.',
    languages: ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh', 'ja', 'ko', 'hi'],
    speed: 'Medium',
    quality: 'Excellent',
    recommended: true,
    minDuration: 6,
  },
  {
    id: 'vits',
    name: 'VITS',
    description: 'Fast, high-quality synthesis. Great balance of speed and quality.',
    languages: ['en', 'es', 'fr', 'de', 'it', 'pt'],
    speed: 'Fast',
    quality: 'Very Good',
    recommended: false,
    minDuration: 10,
  },
  {
    id: 'tacotron2',
    name: 'Tacotron 2',
    description: 'Classic TTS model. Fast and reliable for English.',
    languages: ['en'],
    speed: 'Very Fast',
    quality: 'Good',
    recommended: false,
    minDuration: 15,
  },
  {
    id: 'glow_tts',
    name: 'Glow-TTS',
    description: 'Lightweight and fast. Good for real-time applications.',
    languages: ['en'],
    speed: 'Very Fast',
    quality: 'Good',
    recommended: false,
    minDuration: 10,
  },
]

const CONSENT_PHRASES = [
  "I consent to clone my voice using EchoForge platform for personal use.",
  "I give permission to create a digital voice model of my voice.",
  "I authorize EchoForge to process my voice recording for voice cloning.",
]

export default function VoiceClone() {
  const navigate = useNavigate()

  const [step, setStep] = useState(1) // 1: info, 2: model, 3: voice, 4: consent
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    language: 'en',
    is_public: false,
    model: 'xtts_v2',
  })
  const [selectedModel, setSelectedModel] = useState(TTS_MODELS[0])
  const [consentPhrase, setConsentPhrase] = useState(CONSENT_PHRASES[0])

  const [voiceAudio, setVoiceAudio] = useState(null)
  const [consentAudio, setConsentAudio] = useState(null)

  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const handleModelSelect = (model) => {
    setSelectedModel(model)
    setFormData({ ...formData, model: model.id })
  }

  const handleSubmit = async () => {
    if (!voiceAudio || !consentAudio) {
      setError('Please record both voice and consent audio')
      return
    }

    setUploading(true)
    setError('')

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('audio_file', voiceAudio, 'voice.wav')
      formDataToSend.append('consent_audio', consentAudio, 'consent.wav')
      formDataToSend.append('name', formData.name)
      formDataToSend.append('description', formData.description)
      formDataToSend.append('consent_phrase', consentPhrase)
      formDataToSend.append('language', formData.language)
      formDataToSend.append('is_public', formData.is_public)

      const response = await voiceAPI.uploadVoice(formDataToSend)

      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload voice')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Clone Your Voice</h1>
        <p>Create a high-quality AI voice model in minutes</p>
      </div>

      {/* Progress Steps */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
        {['Info', 'Model', 'Voice', 'Consent'].map((label, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: step > idx + 1 ? 'var(--success)' : step === idx + 1 ? 'var(--primary)' : 'var(--bg-hover)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600,
              transition: 'all 0.3s'
            }}>
              {step > idx + 1 ? '✓' : idx + 1}
            </div>
            <span style={{ color: step === idx + 1 ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
              {label}
            </span>
            {idx < 3 && <span style={{ color: 'var(--text-secondary)', margin: '0 0.5rem' }}>→</span>}
          </div>
        ))}
      </div>

      {error && (
        <div className="status-message status-error">
          {error}
        </div>
      )}

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <div className="card">
          <h2>Voice Profile Information</h2>

          <div className="form-group">
            <label className="form-label">Voice Name *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., My Professional Voice"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input form-textarea"
              placeholder="Describe this voice (optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Primary Language *</label>
            <select
              className="form-input"
              value={formData.language}
              onChange={(e) => setFormData({ ...formData, language: e.target.value })}
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
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              />
              <span>Make this voice public in the Voice Library</span>
            </label>
            <small className="text-muted">Others can use your voice with proper attribution</small>
          </div>

          <button
            className="btn btn-primary"
            onClick={() => setStep(2)}
            disabled={!formData.name}
          >
            Continue to Model Selection
          </button>
        </div>
      )}

      {/* Step 2: Model Selection */}
      {step === 2 && (
        <div className="card">
          <h2>Choose TTS Model</h2>
          <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
            Select the model that best fits your needs. Each model has different strengths.
          </p>

          <div style={{ display: 'grid', gap: '1rem' }}>
            {TTS_MODELS.map((model) => (
              <div
                key={model.id}
                onClick={() => handleModelSelect(model)}
                style={{
                  border: `2px solid ${selectedModel.id === model.id ? 'var(--primary)' : 'var(--border)'}`,
                  borderRadius: '0.75rem',
                  padding: '1.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  background: selectedModel.id === model.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                  position: 'relative'
                }}
              >
                {model.recommended && (
                  <span className="badge badge-success" style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
                    Recommended
                  </span>
                )}

                <h3 style={{ marginBottom: '0.5rem' }}>{model.name}</h3>
                <p className="text-muted" style={{ marginBottom: '1rem' }}>
                  {model.description}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
                  <div>
                    <div className="text-muted">Speed</div>
                    <div style={{ fontWeight: 600 }}>{model.speed}</div>
                  </div>
                  <div>
                    <div className="text-muted">Quality</div>
                    <div style={{ fontWeight: 600 }}>{model.quality}</div>
                  </div>
                  <div>
                    <div className="text-muted">Min. Duration</div>
                    <div style={{ fontWeight: 600 }}>{model.minDuration}s</div>
                  </div>
                </div>

                <div style={{ marginTop: '1rem' }}>
                  <div className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                    Supported Languages:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                    {model.languages.slice(0, 8).map(lang => (
                      <span key={lang} style={{
                        padding: '0.125rem 0.5rem',
                        background: 'var(--bg-hover)',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem'
                      }}>
                        {lang.toUpperCase()}
                      </span>
                    ))}
                    {model.languages.length > 8 && (
                      <span style={{
                        padding: '0.125rem 0.5rem',
                        color: 'var(--text-secondary)',
                        fontSize: '0.75rem'
                      }}>
                        +{model.languages.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button className="btn btn-secondary" onClick={() => setStep(1)}>
              Back
            </button>
            <button className="btn btn-primary" onClick={() => setStep(3)}>
              Continue to Voice Recording
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Voice Recording */}
      {step === 3 && (
        <div className="card">
          <h2>Record Your Voice</h2>
          <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
            Record at least {selectedModel.minDuration} seconds of clear speech. Read naturally and expressively.
          </p>

          <div className="status-message status-info">
            <strong>Tips for best results:</strong>
            <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
              <li>Use a quiet environment</li>
              <li>Speak naturally and clearly</li>
              <li>Vary your intonation and expression</li>
              <li>Avoid background noise</li>
              <li>Stay consistent in volume</li>
            </ul>
          </div>

          <AudioRecorder
            onRecordingComplete={setVoiceAudio}
            minDuration={selectedModel.minDuration}
            label="Voice Sample"
          />

          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button className="btn btn-secondary" onClick={() => setStep(2)}>
              Back
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setStep(4)}
              disabled={!voiceAudio}
            >
              Continue to Consent
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Consent Recording */}
      {step === 4 && (
        <div className="card">
          <h2>Consent Verification</h2>
          <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
            For ethical compliance, please record yourself speaking the consent phrase below.
          </p>

          <div className="form-group">
            <label className="form-label">Consent Phrase</label>
            <select
              className="form-input"
              value={consentPhrase}
              onChange={(e) => setConsentPhrase(e.target.value)}
            >
              {CONSENT_PHRASES.map((phrase, idx) => (
                <option key={idx} value={phrase}>{phrase}</option>
              ))}
            </select>
          </div>

          <div className="status-message status-info">
            <strong>Please read this phrase clearly:</strong>
            <p style={{ fontSize: '1.1rem', marginTop: '0.5rem', fontWeight: 600 }}>
              "{consentPhrase}"
            </p>
          </div>

          <AudioRecorder
            onRecordingComplete={setConsentAudio}
            minDuration={3}
            maxDuration={30}
            label="Consent Recording"
          />

          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button className="btn btn-secondary" onClick={() => setStep(3)} disabled={uploading}>
              Back
            </button>
            <button
              className="btn btn-success"
              onClick={handleSubmit}
              disabled={!consentAudio || uploading}
            >
              {uploading ? 'Uploading...' : 'Create Voice Profile'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
