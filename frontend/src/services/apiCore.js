import axios from 'axios'

// en local apunta al Django local, en producción al backend de Vercel
const isLocal = typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
const _apiBase = import.meta.env.VITE_API_URL ||
  (isLocal ? 'http://127.0.0.1:8000/api' : `${window.location.origin}/_/backend/api`)

// cliente axios principal para la API general del backend
const apiCore = axios.create({
  baseURL: _apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

// interceptor que mete el token en cada petición si lo tenemos guardado
apiCore.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // si mandamos FormData dejamos que el navegador ponga el Content-Type él solo
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default apiCore