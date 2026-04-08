import apiCore from '@/services/apiCore'

export async function getHomeGymsService(filters = {}) {
  const params = {}

  if (filters.city) {
    params.city = filters.city
  }

  if (filters.postal_code) {
    params.postal_code = filters.postal_code
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