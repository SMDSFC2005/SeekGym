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
    // carga los gyms con los filtros activos, combinando los nuevos con los guardados
    async fetchHomeGyms(filters = {}) {
      this.loading = true
      this.error = ''

      // mezclamos los filtros nuevos con los que ya tenía el store
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

    // carga el detalle completo de un gym por su slug
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

    // pilla el gym del usuario logueado si tiene uno
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

    // crea un gym nuevo y lo guarda en myGym
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

    // actualiza el gym y sincroniza gymDetail y myGym si corresponde
    async updateGym(slug, payload) {
      this.saveLoading = true
      this.saveError = ''

      const response = await updateGymService(slug, payload)
      this.saveLoading = false

      if (response?.status === 200) {
        this.gymDetail = response.data

        // si el gym editado es el nuestro, actualizamos myGym también
        if (this.myGym && this.myGym.slug === slug) {
          this.myGym = response.data
        }

        return { isOk: true, data: response.data }
      }

      this.saveError = response?.data?.detail || 'No se pudo actualizar el gimnasio.'
      return { isOk: false, data: response?.data || null }
    },

    // publica un anuncio y recarga el detalle del gym para que se vea al momento
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

    // carga la lista de provincias para los filtros
    async fetchProvinces() {
      const response = await getProvincesService()

      if (response?.status === 200) {
        this.provinces = response.data || []
        return { isOk: true, data: response.data }
      }

      this.provinces = []
      return { isOk: false, data: response?.data || null }
    },

    // carga los municipios de una provincia, si no hay ID limpiamos la lista
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

    // limpia los municipios, útil al cambiar de provincia
    resetMunicipalities() {
      this.municipalities = []
    },
  },
})
