import { defineStore } from 'pinia'
import {
  getHomeGymsService,
  getGymDetailService,
  getMyGymService,
  createGymService,
  updateGymService,
  createGymAnnouncementService,
  getProvincesService,
  getMunicipalitiesService,
} from '../services/gymsService'

export const useGymsStore = defineStore('gyms', {
  state: () => ({
    gyms: [],
    gymDetail: null,
    myGym: null,

    loading: false,
    detailLoading: false,
    myGymLoading: false,
    saveLoading: false,
    announcementLoading: false,

    error: '',
    detailError: '',
    myGymError: '',
    saveError: '',
    announcementError: '',

    provinces: [],
    municipalities: [],

    currentFilters: {
      province_id: '',
      municipality_id: '',
      search: '',
    },
  }),

  actions: {
    async fetchHomeGyms(filters = {}) {
      this.loading = true
      this.error = ''

      const finalFilters = {
        province_id: filters.province_id ?? this.currentFilters.province_id,
        municipality_id: filters.municipality_id ?? this.currentFilters.municipality_id,
        search: filters.search ?? this.currentFilters.search,
      }

      const response = await getHomeGymsService(finalFilters)
      this.loading = false

      if (response?.status === 200) {
        this.gyms = response.data.results || []
        this.currentFilters = finalFilters

        return { isOk: true, data: response.data }
      }

      this.gyms = []
      this.error = 'No se pudieron cargar los gimnasios.'
      return { isOk: false, data: response?.data || null }
    },

    async fetchGymDetail(slug) {
      this.detailLoading = true
      this.detailError = ''
      this.gymDetail = null

      const response = await getGymDetailService(slug)
      this.detailLoading = false

      if (response?.status === 200) {
        this.gymDetail = response.data
        return { isOk: true, data: response.data }
      }

      this.detailError = 'No se pudo cargar el detalle del gimnasio.'
      return { isOk: false, data: response?.data || null }
    },

    async fetchMyGym() {
      this.myGymLoading = true
      this.myGymError = ''

      const response = await getMyGymService()
      this.myGymLoading = false

      if (response?.status === 200) {
        this.myGym = response.data.gym
        return { isOk: true, data: response.data }
      }

      this.myGym = null
      this.myGymError = 'No se pudo cargar tu gimnasio.'
      return { isOk: false, data: response?.data || null }
    },

    async createGym(payload) {
      this.saveLoading = true
      this.saveError = ''

      const response = await createGymService(payload)
      this.saveLoading = false

      if (response?.status === 201) {
        this.myGym = response.data
        return { isOk: true, data: response.data }
      }

      this.saveError = response?.data?.detail || 'No se pudo crear el gimnasio.'
      return { isOk: false, data: response?.data || null }
    },

    async updateGym(slug, payload) {
      this.saveLoading = true
      this.saveError = ''

      const response = await updateGymService(slug, payload)
      this.saveLoading = false

      if (response?.status === 200) {
        this.gymDetail = response.data

        if (this.myGym && this.myGym.slug === slug) {
          this.myGym = response.data
        }

        return { isOk: true, data: response.data }
      }

      this.saveError = response?.data?.detail || 'No se pudo actualizar el gimnasio.'
      return { isOk: false, data: response?.data || null }
    },

    async createAnnouncement(slug, payload) {
      this.announcementLoading = true
      this.announcementError = ''

      const response = await createGymAnnouncementService(slug, payload)
      this.announcementLoading = false

      if (response?.status === 201) {
        await this.fetchGymDetail(slug)
        if (this.myGym && this.myGym.slug === slug) {
          await this.fetchMyGym()
        }

        return { isOk: true, data: response.data }
      }

      this.announcementError = response?.data?.detail || 'No se pudo crear la publicación.'
      return { isOk: false, data: response?.data || null }
    },

    async fetchProvinces() {
      const response = await getProvincesService()

      if (response?.status === 200) {
        this.provinces = response.data || []
        return { isOk: true, data: response.data }
      }

      this.provinces = []
      return { isOk: false, data: response?.data || null }
    },

    async fetchMunicipalities(provinceId) {
      if (!provinceId) {
        this.municipalities = []
        return { isOk: true, data: [] }
      }

      const response = await getMunicipalitiesService(provinceId)

      if (response?.status === 200) {
        this.municipalities = response.data || []
        return { isOk: true, data: response.data }
      }

      this.municipalities = []
      return { isOk: false, data: response?.data || null }
    },

    resetMunicipalities() {
      this.municipalities = []
    },
  },
})
