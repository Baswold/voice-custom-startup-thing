import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const auth = JSON.parse(localStorage.getItem('echoforge-auth') || '{}')
  if (auth.state?.token) {
    config.headers.Authorization = `Bearer ${auth.state.token}`
  }
  return config
})

// Auth API
export const authAPI = {
  register: (data) => apiClient.post('/api/users/register', data),
  login: (data) => apiClient.post('/api/users/login', data),
  getMe: () => apiClient.get('/api/users/me'),
}

// Voice API
export const voiceAPI = {
  uploadVoice: (formData) => apiClient.post('/api/voices/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  listVoices: () => apiClient.get('/api/voices'),
  getVoice: (id) => apiClient.get(`/api/voices/${id}`),
}

// Job API
export const jobAPI = {
  getJob: (id) => apiClient.get(`/api/jobs/${id}`),
  listJobs: (limit = 50) => apiClient.get(`/api/jobs?limit=${limit}`),
}

// Synthesis API
export const synthesisAPI = {
  synthesize: (data) => apiClient.post('/api/synthesize', data),
}

export default apiClient
