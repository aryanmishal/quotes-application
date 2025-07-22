import axios from 'axios'
import { Quote } from './store/quotes'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
})

// Add auth token to requests if it exists
api.interceptors.request.use((config) => {
  // Check both localStorage and sessionStorage for the auth token
  const getToken = () => {
    if (typeof window === 'undefined') return null
    
    // Try localStorage first
    const persistentToken = localStorage.getItem('auth-storage')
    if (persistentToken) {
      try {
        const parsed = JSON.parse(persistentToken)
        if (parsed.state.token) return parsed.state.token
      } catch (error) {
        console.error('Error parsing persistent auth token:', error)
      }
    }
    
    // Try sessionStorage if localStorage token not found
    const sessionToken = sessionStorage.getItem('auth-storage')
    if (sessionToken) {
      try {
        const parsed = JSON.parse(sessionToken)
        if (parsed.state.token) return parsed.state.token
      } catch (error) {
        console.error('Error parsing session auth token:', error)
      }
    }
    
    return null
  }

  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth storage
      localStorage.removeItem('auth-storage')
      sessionStorage.removeItem('auth-storage')
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)  // OAuth2 expects 'username' field
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },
  register: async (name: string, email: string, password: string) => {
    const response = await api.post('/auth/register', { name, email, password })
    return response.data
  },
  updateTheme: async (theme: string) => {
    const response = await api.post(`/auth/update-theme?theme=${theme}`)
    return response.data
  },
}

export const quotesAPI = {
  getQuotes: async () => {
    const response = await api.get('/quotes')
    return response.data
  },
  getQuote: async (id: string) => {
    const response = await api.get(`/quotes/${id}`)
    return response.data
  },
  createQuote: async (quote: Omit<Quote, '_id'>) => {
    const response = await api.post('/quotes', quote)
    return response.data
  },
  updateQuote: async (id: string, quote: Partial<Quote>) => {
    const response = await api.patch(`/quotes/${id}`, quote)
    return response.data
  },
  deleteQuote: async (id: string) => {
    const response = await api.delete(`/quotes/${id}`)
    return response.data
  },
  likeQuote: async (id: string) => {
    const response = await api.post(`/quotes/${id}/likes/up`)
    return response.data
  },
  dislikeQuote: async (id: string) => {
    const response = await api.post(`/quotes/${id}/dislike/up`)
    return response.data
  },
  getQuoteReactions: async (id: string) => {
    const response = await api.get(`/quotes/${id}/reactions`)
    return response.data
  },
} 