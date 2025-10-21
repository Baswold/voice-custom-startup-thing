import { useState } from 'react'

export default function VoiceLibrary() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState('all')

  // Placeholder for future implementation
  const publicVoices = []

  return (
    <div className="container">
      <div className="header">
        <h1>Voice Library</h1>
        <p>Explore community-contributed voices (Coming Soon)</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search voices..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: 1 }}
          />

          <select
            className="form-input"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            style={{ width: '200px' }}
          >
            <option value="all">All Languages</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
          </select>
        </div>

        <div style={{ textAlign: 'center', padding: '4rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎤</div>
          <h2>Voice Library Coming Soon</h2>
          <p className="text-muted" style={{ marginTop: '1rem', maxWidth: '600px', margin: '1rem auto' }}>
            The public voice library will allow users to share their voices with the community.
            Each voice will include proper attribution, licensing information, and usage terms.
          </p>

          <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>Features in Development:</div>
            <ul style={{ textAlign: 'left', color: 'var(--text-secondary)' }}>
              <li>Browse community voices by language, style, and genre</li>
              <li>Preview voices before using them</li>
              <li>Proper attribution and licensing (CC-BY, CC-BY-SA, etc.)</li>
              <li>Rating and review system</li>
              <li>Creator profiles and revenue sharing</li>
              <li>Advanced search and filtering</li>
            </ul>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <a href="/clone" className="btn btn-primary">
              Create Your Own Voice
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
