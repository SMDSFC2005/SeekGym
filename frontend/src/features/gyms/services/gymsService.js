import apiCore from '@/services/apiCore'

// pide los gyms de la home con los filtros que vengan, solo añade los que tengan valor
export async function getHomeGymsService(filters = {}) {
  const params = {}

  if (filters.province_id) {
    params.province_id = filters.province_id
  }

  if (filters.municipality_id) {
    params.municipality_id = filters.municipality_id
  }

  if (filters.search) {
    params.search = filters.search
  }

  try {
    return await apiCore.get('/gyms/home/', { params })
  } catch (error) {
    return error.response
  }
}

// pide el detalle completo de un gym por su slug
export async function getGymDetailService(slug) {
  try {
    return await apiCore.get(`/gyms/${slug}/`)
  } catch (error) {
    return error.response
  }
}

// pide el gym del usuario logueado
export async function getMyGymService() {
  try {
    return await apiCore.get('/gyms/my-gym/')
  } catch (error) {
    return error.response
  }
}

// crea un gym nuevo con los datos del formulario
export async function createGymService(payload) {
  try {
    return await apiCore.post('/gyms/create/', payload)
  } catch (error) {
    return error.response
  }
}

// actualiza parcialmente un gym existente (PATCH para mandar solo lo que cambia)
export async function updateGymService(slug, payload) {
  try {
    return await apiCore.patch(`/gyms/${slug}/manage/`, payload)
  } catch (error) {
    return error.response
  }
}

// borra un gym permanentemente
export async function deleteGymService(slug) {
  try {
    return await apiCore.delete(`/gyms/${slug}/manage/`)
  } catch (error) {
    return error.response
  }
}

// publica un anuncio en el gym indicado
export async function createGymAnnouncementService(slug, payload) {
  try {
    return await apiCore.post(`/gyms/${slug}/announcements/`, payload)
  } catch (error) {
    return error.response
  }
}

// lista de provincias para los filtros del buscador
export async function getProvincesService() {
  try {
    return await apiCore.get('/gyms/filters/provinces/')
  } catch (error) {
    return error.response
  }
}

// municipios de una provincia concreta
export async function getMunicipalitiesService(provinceId) {
  try {
    return await apiCore.get('/gyms/filters/municipalities/', {
      params: { province_id: provinceId },
    })
  } catch (error) {
    return error.response
  }
}

// códigos postales disponibles según los filtros de provincia/municipio
export async function getPostalCodesService(filters = {}) {
  const params = {}

  if (filters.province_id) {
    params.province_id = filters.province_id
  }

  if (filters.municipality_id) {
    params.municipality_id = filters.municipality_id
  }

  try {
    return await apiCore.get('/gyms/filters/postal-codes/', { params })
  } catch (error) {
    return error.response
  }
}

// gyms que sigue el usuario logueado
export async function getFollowedGymsService() {
  try {
    return await apiCore.get('/gyms/seguidos/')
  } catch (error) {
    return error.response
  }
}

// toggle seguir/dejar de seguir un gym
export async function toggleFollowGymService(slug) {
  try {
    return await apiCore.post(`/gyms/${slug}/follow/`)
  } catch (error) {
    return error.response
  }
}

// pilla las notificaciones pendientes del usuario
export async function getNotificationsService() {
  try {
    return await apiCore.get('/gyms/notifications/')
  } catch (error) {
    return error.response
  }
}

// marca todas las notificaciones como leídas
export async function markNotificationsReadService() {
  try {
    return await apiCore.post('/gyms/notifications/')
  } catch (error) {
    return error.response
  }
}

// sube la imagen de portada del gym como FormData
export async function uploadGymImageService(slug, file) {
  const formData = new FormData()
  formData.append('image', file)
  try {
    return await apiCore.post(`/gyms/${slug}/upload-image/`, formData)
  } catch (error) {
    return error.response
  }
}