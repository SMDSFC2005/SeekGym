import api from '@/services/api'
import apiPrivate from '@/services/apiPrivate'

export async function loginService(credentials) {
  try {
    return await api.post('/login/', credentials)
  } catch (error) {
    return error.response
  }
}

export async function registerService(userData) {
  try {
    return await api.post('/register/', userData)
  } catch (error) {
    return error.response
  }
}

export async function meService() {
  try {
    return await apiPrivate.get('/me/')
  } catch (error) {
    return error.response
  }
}

export async function refreshService(refresh) {
  try {
    return await api.post('/refresh/', { refresh })
  } catch (error) {
    return error.response
  }
}