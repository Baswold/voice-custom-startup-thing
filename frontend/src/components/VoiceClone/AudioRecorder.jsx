import { useState, useRef, useEffect } from 'react'

export default function AudioRecorder({ onRecordingComplete, minDuration = 6, maxDuration = 120, label = "Recording" }) {
  const [isRecording, setIsRecording] = useState(false)
  const [duration, setDuration] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioURL, setAudioURL] = useState(null)

  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
        setAudioBlob(blob)
        setAudioURL(URL.createObjectURL(blob))
        onRecordingComplete(blob)

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setDuration(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          const newDuration = prev + 0.1
          if (newDuration >= maxDuration) {
            stopRecording()
            return maxDuration
          }
          return newDuration
        })
      }, 100)

    } catch (err) {
      console.error('Error accessing microphone:', err)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)

      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const resetRecording = () => {
    setAudioBlob(null)
    setAudioURL(null)
    setDuration(0)
    onRecordingComplete(null)
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = (seconds % 60).toFixed(1)
    return `${mins}:${secs.padStart(4, '0')}`
  }

  const canStop = duration >= minDuration

  return (
    <div className="audio-recorder">
      {isRecording && (
        <div className="recording-indicator">
          <div className="recording-dot"></div>
          <span>Recording</span>
        </div>
      )}

      <div className="waveform">
        {isRecording ? (
          <div className="waveform-bars">
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
            <div className="waveform-bar"></div>
          </div>
        ) : audioURL ? (
          <audio src={audioURL} controls style={{ width: '100%' }} />
        ) : (
          <div className="text-muted">Click the button below to start recording</div>
        )}
      </div>

      <div className="timer">
        {formatTime(duration)}
      </div>

      {isRecording && (
        <div className="text-muted" style={{ marginBottom: '1rem' }}>
          {duration < minDuration ? (
            <>Minimum: {formatTime(minDuration)}</>
          ) : (
            <>Recording... (max: {formatTime(maxDuration)})</>
          )}
        </div>
      )}

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        {!isRecording && !audioBlob && (
          <button className="btn btn-danger" onClick={startRecording}>
            🎤 Start Recording
          </button>
        )}

        {isRecording && (
          <button
            className="btn btn-success"
            onClick={stopRecording}
            disabled={!canStop}
          >
            ⏹ Stop Recording
          </button>
        )}

        {audioBlob && (
          <>
            <button className="btn btn-success" disabled>
              ✓ Recording Complete ({formatTime(duration)})
            </button>
            <button className="btn btn-secondary" onClick={resetRecording}>
              🔄 Record Again
            </button>
          </>
        )}
      </div>
    </div>
  )
}
