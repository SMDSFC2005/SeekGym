import { defineStore } from 'pinia'
import {
  getHomeGymsService,
  getGymDetailService,
} from '../services/gymsService'

export const useGymsStore = defineStore('gyms', {
  state: () => ({
    gyms: [],
    gymDetail: null,

    loading: false,
    detailLoading: false,

    error: '',
    detailError: '',

    currentFilters: {
      city: 'Sevilla',
      postal_code: '',
    },
  }),

  actions: {
    async fetchHomeGyms(filters = {}) {
      this.loading = true
      this.error = ''

      const finalFilters = {
        city: filters.city ?? this.currentFilters.city,
        postal_code: filters.postal_code ?? this.currentFilters.postal_code,
      }

      const response = await getHomeGymsService(finalFilters)

      this.loading = false

      if (response?.status === 200) {
        this.gyms = response.data.results || []
        this.currentFilters = finalFilters

        return {
          isOk: true,
          message: 'Gimnasios cargados correctamente',
          data: response.data,
        }
      }

      this.gyms = []
      this.error = 'No se pudieron cargar los gimnasios.'

      return {
        isOk: false,
        message: 'No se pudieron cargar los gimnasios.',
        data: response?.data || null,
      }
    },

    async fetchGymDetail(slug) {
      this.detailLoading = true
      this.detailError = ''
      this.gymDetail = null

      const response = await getGymDetailService(slug)

      this.detailLoading = false

      if (response?.status === 200) {
        this.gymDetail = response.data

        return {
          isOk: true,
          message: 'Gimnasio cargado correctamente',
          data: response.data,
        }
      }

      this.detailError = 'No se pudo cargar el detalle del gimnasio.'

      return {
        isOk: false,
        message: 'No se pudo cargar el detalle del gimnasio.',
        data: response?.data || null,
      }
    },
  },
})