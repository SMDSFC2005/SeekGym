import api from '@/services/api'
import apiPrivate from '@/services/apiPrivate'

// manda las credenciales y pilla los tokens si todo va bien
export async function loginService(credentials) {
  try {
    return await api.post('/login/', credentials)
  } catch (error) {
    return error.response
  }
}

// crea una cuenta nueva con los datos del usuario
export async function registerService(userData) {
  try {
    return await api.post('/register/', userData)
  } catch (error) {
    return error.response
  }
}

// devuelve los datos del usuario logueado usando el token guardado
export async function meService() {
  try {
    return await apiPrivate.get('/me/')
  } catch (error) {
    return error.response
  }
}

// renueva el access token usando el refresh token
export async function refreshService(refresh) {
  try {
    return await api.post('/refresh/', { refresh })
  } catch (error) {
    return error.response
  }
}

// sube una foto de perfil como FormData para que el backend la procese
export async function uploadProfilePhotoService(file) {
  const formData = new FormData()
  formData.append('photo', file)
  try {
    return await apiPrivate.post('/me/photo/', formData)
  } catch (error) {
    return error.response
  }
}