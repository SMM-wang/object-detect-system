import { defineStore } from 'pinia'
import { loginApi } from '@/services/auth'
import { getStorageItem, removeStorageItem, setStorageItem, TOKEN_KEY, USER_KEY } from '@/utils/storage'
import { ROLES } from '@/constants'

function normalizeSession(data) {
  const token = data?.token || data?.accessToken || data?.jwt || ''
  const user = data?.user || data?.sysUser || data || {}
  const role = user.role || user.roleCode || data?.role || ROLES.USER
  return { token, user: { ...user, role }, role }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    user: null,
    role: ROLES.USER
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    isAdmin: (state) => state.role === ROLES.ADMIN,
    displayName: (state) => state.user?.nickname || state.user?.name || state.user?.username || '用户'
  },
  actions: {
    hydrateFromStorage() {
      this.token = getStorageItem(TOKEN_KEY, '')
      this.user = getStorageItem(USER_KEY, null)
      this.role = this.user?.role || ROLES.USER
    },
    setSession(session) {
      this.token = session.token
      this.user = session.user
      this.role = session.role
      setStorageItem(TOKEN_KEY, session.token)
      setStorageItem(USER_KEY, session.user)
    },
    clearSession() {
      this.token = ''
      this.user = null
      this.role = ROLES.USER
      removeStorageItem(TOKEN_KEY)
      removeStorageItem(USER_KEY)
    },
    async login(payload) {
      const data = await loginApi(payload)
      const session = normalizeSession(data)
      this.setSession(session)
      return session
    },
    logout() {
      this.clearSession()
    }
  }
})
