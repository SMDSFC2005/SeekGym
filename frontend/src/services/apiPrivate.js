import axios from 'axios'

// en local apunta al Django local, en producción al backend de Vercel
const isLocal = typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
const _apiAuthBase = import.meta.env.VITE_API_AUTH_URL ||
  (isLocal ? 'http://127.0.0.1:8000/api/auth' : `${window.location.origin}/_/backend/api/auth`)

// cliente axios para los endpoints de autenticación (/api/auth/...)
const apiPrivate = axios.create({
  baseURL: _apiAuthBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

// igual que en apiCore, metemos el token si lo tenemos
apiPrivate.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // para subir fotos de perfil dejamos que el browser gestione el Content-Type
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default apiPrivate