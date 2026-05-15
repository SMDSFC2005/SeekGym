import { defineStore } from 'pinia'
import {
  loginService,
  registerService,
  meService,
  refreshService,
} from '../services/authService'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
  }),

  actions: {
    // login: pide tokens, los guarda y carga los datos del usuario
    async login(username, password) {
      const response = await loginService({ username, password })

      if (response?.status === 200) {
        const { access, refresh } = response.data

        // guardamos los dos tokens en localStorage
        localStorage.setItem('access', access)
        localStorage.setItem('refresh', refresh)

        const meResponse = await meService()

        if (meResponse?.status === 200) {
          this.user = meResponse.data
          this.isAuthenticated = true

          return {
            isOk: true,
            message: 'Login correcto',
            data: meResponse.data,
          }
        }

        return {
          isOk: false,
          message: 'No se pudo obtener el usuario autenticado',
          data: null,
        }
      }

      return {
        isOk: false,
        message: 'Credenciales incorrectas',
        data: null,
      }
    },

    // registro de usuario nuevo, por defecto rol NORMAL
    async register(username, password, email = '', rol = 'NORMAL') {
      const response = await registerService({
        username,
        password,
        email,
        rol,
      })

      if (response?.status === 201) {
        return {
          isOk: true,
          message: 'Usuario registrado correctamente',
          data: response.data,
        }
      }

      return {
        isOk: false,
        message: 'No se pudo registrar el usuario',
        data: response?.data || null,
      }
    },

    // comprueba si hay sesión activa al arrancar la app, e intenta refrescar el token si hace falta
    async checkAuthentication() {
      const token = localStorage.getItem('access')

      // si no hay token ni intentamos, nos quedamos como no autenticados
      if (!token) {
        this.user = null
        this.isAuthenticated = false
        return
      }

      const response = await meService()

      if (response?.status === 200) {
        this.user = response.data
        this.isAuthenticated = true
        return
      }

      const refresh = localStorage.getItem('refresh')

      // si tampoco hay refresh token, pues logout directamente
      if (!refresh) {
        this.logout()
        return
      }

      // intentamos renovar el access token con el refresh
      const refreshResponse = await refreshService(refresh)

      if (refreshResponse?.status === 200) {
        localStorage.setItem('access', refreshResponse.data.access)

        // con el nuevo token volvemos a pedir los datos del usuario
        const retryMe = await meService()

        if (retryMe?.status === 200) {
          this.user = retryMe.data
          this.isAuthenticated = true
          return
        }
      }

      this.logout()
    },

    // limpia todo: tokens y estado del usuario
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.user = null
      this.isAuthenticated = false
    },
  },
})