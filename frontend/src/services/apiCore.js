import axios from 'axios'

// cliente axios principal para la API general del backend
const apiCore = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
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
