import { defineStore } from 'pinia'
import {
  getHomeGymsService,
  getGymDetailService,
  getProvincesService,
  getMunicipalitiesService,
  getPostalCodesService,
} from '../services/gymsService'

export const useGymsStore = defineStore('gyms', {
  state: () => ({
    gyms: [],
    gymDetail: null,

    loading: false,
    detailLoading: false,

    error: '',
    detailError: '',

    provinces: [],
    municipalities: [],
    postalCodes: [],

    currentFilters: {
      province_id: '',
      municipality_id: '',
      postal_code: '',
    },
  }),

  actions: {
    async fetchHomeGyms(filters = {}) {
      this.loading = true
      this.error = ''

      const finalFilters = {
        province_id: filters.province_id ?? this.currentFilters.province_id,
        municipality_id: filters.municipality_id ?? this.currentFilters.municipality_id,
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

    async fetchProvinces() {
      const response = await getProvincesService()

      if (response?.status === 200) {
        this.provinces = response.data || []
        return {
          isOk: true,
          data: response.data,
        }
      }

      this.provinces = []
      return {
        isOk: false,
        data: response?.data || null,
      }
    },

    async fetchMunicipalities(provinceId) {
      if (!provinceId) {
        this.municipalities = []
        return {
          isOk: true,
          data: [],
        }
      }

      const response = await getMunicipalitiesService(provinceId)

      if (response?.status === 200) {
        this.municipalities = response.data || []
        return {
          isOk: true,
          data: response.data,
        }
      }

      this.municipalities = []
      return {
        isOk: false,
        data: response?.data || null,
      }
    },

    async fetchPostalCodes(filters = {}) {
      if (!filters.province_id || !filters.municipality_id) {
        this.postalCodes = []
        return {
          isOk: true,
          data: [],
        }
      }

      const response = await getPostalCodesService(filters)

      if (response?.status === 200) {
        this.postalCodes = response.data || []
        return {
          isOk: true,
          data: response.data,
        }
      }

      this.postalCodes = []
      return {
        isOk: false,
        data: response?.data || null,
      }
    },

    resetMunicipalities() {
      this.municipalities = []
    },

    resetPostalCodes() {
      this.postalCodes = []
    },
  },
})