import { defineStore } from 'pinia'
import { getNotificationsService, markNotificationsReadService } from '@/features/gyms/services/gymsService'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    pendingRequests: 0,
    unreadAnnouncements: [],
  }),

  getters: {
    total(state) {
      return state.pendingRequests + state.unreadAnnouncements.length
    },
  },

  actions: {
    async fetch() {
      const response = await getNotificationsService()
      if (response?.status === 200) {
        this.pendingRequests = response.data.pending_requests ?? 0
        this.unreadAnnouncements = response.data.unread_announcements ?? []
      }
    },

    async markRead() {
      await markNotificationsReadService()
      this.unreadAnnouncements = []
    },
  },
})
