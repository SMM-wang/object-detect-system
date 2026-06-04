import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    loadingCount: 0,
    lastError: ''
  }),
  getters: {
    isLoading: (state) => state.loadingCount > 0
  },
  actions: {
    startLoading() {
      this.loadingCount += 1
    },
    stopLoading() {
      this.loadingCount = Math.max(0, this.loadingCount - 1)
    },
    setError(error) {
      this.lastError = error?.message || String(error || '')
    },
    clearError() {
      this.lastError = ''
    }
  }
})
