import { defineStore } from 'pinia'
import { api, getToken, setToken } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, ready: false }),
  getters: {
    isLoggedIn: (state) => !!state.user,
    roles: (state) => state.user?.roles ?? [],
    isAdmin() {
      return this.roles.includes('admin')
    },
    otpSetupRequired: (state) => !!state.user?.otp_setup_required,
    canEdit() {
      return this.isAdmin || this.roles.includes('user')
    },
  },
  actions: {
    async init() {
      if (getToken()) {
        try {
          await this.fetchMe()
        } catch {
          this.clear()
        }
      }
      this.ready = true
    },
    async fetchMe() {
      this.user = await api('/users/me')
    },
    async login(username, password, otp) {
      const data = await api('/auth/login', {
        method: 'POST',
        body: { username, password, otp: otp || null },
        auth: false,
      })
      await this.acceptToken(data.access_token)
    },
    async acceptToken(token) {
      setToken(token)
      await this.fetchMe()
    },
    clear() {
      setToken(null)
      this.user = null
    },
    logout() {
      this.clear()
    },
  },
})
