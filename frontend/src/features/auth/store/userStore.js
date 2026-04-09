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
    async login(username, password) {
      const response = await loginService({ username, password })

      if (response?.status === 200) {
        const { access, refresh } = response.data

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

    async checkAuthentication() {
      const token = localStorage.getItem('access')

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

      if (!refresh) {
        this.logout()
        return
      }

      const refreshResponse = await refreshService(refresh)

      if (refreshResponse?.status === 200) {
        localStorage.setItem('access', refreshResponse.data.access)

        const retryMe = await meService()

        if (retryMe?.status === 200) {
          this.user = retryMe.data
          this.isAuthenticated = true
          return
        }
      }

      this.logout()
    },

    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.user = null
      this.isAuthenticated = false
    },
  },
})