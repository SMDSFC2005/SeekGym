import axios from 'axios'

// cliente axios para los endpoints de autenticación (/api/auth/...)
const apiPrivate = axios.create({
  baseURL: '/api/auth',
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