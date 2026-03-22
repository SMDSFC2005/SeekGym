import { defineStore } from 'pinia'
import { getHomeGymsService } from '../services/gymsService'

export const useGymsStore = defineStore('gyms', {
  state: () => ({
    gyms: [],
    loading: false,
    error: '',
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
  },
})