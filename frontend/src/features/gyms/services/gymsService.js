import apiCore from '@/services/apiCore'

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

export async function getGymDetailService(slug) {
  try {
    return await apiCore.get(`/gyms/${slug}/`)
  } catch (error) {
    return error.response
  }
}

export async function getMyGymService() {
  try {
    return await apiCore.get('/gyms/my-gym/')
  } catch (error) {
    return error.response
  }
}

export async function createGymService(payload) {
  try {
    return await apiCore.post('/gyms/create/', payload)
  } catch (error) {
    return error.response
  }
}

export async function updateGymService(slug, payload) {
  try {
    return await apiCore.patch(`/gyms/${slug}/manage/`, payload)
  } catch (error) {
    return error.response
  }
}

export async function deleteGymService(slug) {
  try {
    return await apiCore.delete(`/gyms/${slug}/manage/`)
  } catch (error) {
    return error.response
  }
}

export async function createGymAnnouncementService(slug, payload) {
  try {
    return await apiCore.post(`/gyms/${slug}/announcements/`, payload)
  } catch (error) {
    return error.response
  }
}

export async function getProvincesService() {
  try {
    return await apiCore.get('/gyms/filters/provinces/')
  } catch (error) {
    return error.response
  }
}

export async function getMunicipalitiesService(provinceId) {
  try {
    return await apiCore.get('/gyms/filters/municipalities/', {
      params: { province_id: provinceId },
    })
  } catch (error) {
    return error.response
  }
}

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

export async function getFollowedGymsService() {
  try {
    return await apiCore.get('/gyms/seguidos/')
  } catch (error) {
    return error.response
  }
}

export async function toggleFollowGymService(slug) {
  try {
    return await apiCore.post(`/gyms/${slug}/follow/`)
  } catch (error) {
    return error.response
  }
}

export async function getNotificationsService() {
  try {
    return await apiCore.get('/gyms/notifications/')
  } catch (error) {
    return error.response
  }
}

export async function markNotificationsReadService() {
  try {
    return await apiCore.post('/gyms/notifications/')
  } catch (error) {
    return error.response
  }
}