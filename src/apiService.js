import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

const withAuth = (token) => (token ? { Authorization: `Bearer ${token}` } : {})

export const login = (credentials) => api.post('/auth/login', credentials)
export const register = (payload) => api.post('/auth/register', payload)
export const fetchMe = (token) => api.get('/auth/me', { headers: withAuth(token) })

export const getDashboardStats = (token) => api.get('/admin/stats', { headers: withAuth(token) })

export const generateGrid = (strategy, token, game = 'euromillions') =>
  api.get(`/generate/${strategy}`, { params: { game }, headers: withAuth(token) })

export const generateMonteCarloFibo = (token, game = 'euromillions') =>
  generateGrid('monte_carlo_fibo', token, game)

export const fetchCampagnes = (token) => api.get('/campagnes/get', { headers: withAuth(token) })

export const fetchDraws = (token, game = 'euromillions') =>
  api.get('/draws/recent', { params: { game }, headers: withAuth(token) })

export const fetchAnalytics = (token, game = 'euromillions') =>
  api.get('/draws/analytics', { params: { game }, headers: withAuth(token) })

export const fetchGamesRegistry = () => api.get('/games/registry')
export const fetchReport = () => api.get('/report/history')
export const fetchHealth = () => api.get('/health')

export default api
