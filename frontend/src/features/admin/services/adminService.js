import apiCore from '@/services/apiCore'

export async function getGymRequestsService() {
  try {
    return await apiCore.get('/auth/gym-requests/')
  } catch (error) {
    return error.response
  }
}

export async function approveGymRequestService(userId) {
  try {
    return await apiCore.post(`/auth/gym-requests/${userId}/approve/`)
  } catch (error) {
    return error.response
  }
}

export async function rejectGymRequestService(userId) {
  try {
    return await apiCore.post(`/auth/gym-requests/${userId}/reject/`)
  } catch (error) {
    return error.response
  }
}
