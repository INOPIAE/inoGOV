import { defineStore } from 'pinia'
import { api, getToken, notifyInactivityTimeout, setToken } from '../api'

const INACTIVITY_TIMEOUT_MS = 60 * 60 * 1000
const TOKEN_REFRESH_INTERVAL_MS = 5 * 60 * 1000
const ACTIVITY_CHECK_INTERVAL_MS = 30 * 1000

let activityInterval = null
let lastActivityAt = 0
let lastTokenRefreshAt = 0
let activityHandler = null
let refreshInFlight = null

function stopActivityTracking() {
  if (activityInterval !== null) clearInterval(activityInterval)
  activityInterval = null
  if (activityHandler) {
    for (const eventName of ['pointerdown', 'pointermove', 'keydown', 'touchstart', 'wheel']) {
      document.removeEventListener(eventName, activityHandler)
    }
  }
  activityHandler = null
}

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
          this.startActivityTracking()
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
      this.startActivityTracking()
    },
    startActivityTracking() {
      stopActivityTracking()
      lastActivityAt = Date.now()
      lastTokenRefreshAt = Date.now()
      activityHandler = () => {
        lastActivityAt = Date.now()
        if (lastActivityAt - lastTokenRefreshAt >= TOKEN_REFRESH_INTERVAL_MS) {
          this.refreshSession().catch(() => {})
        }
      }
      for (const eventName of ['pointerdown', 'pointermove', 'keydown', 'touchstart', 'wheel']) {
        document.addEventListener(eventName, activityHandler, { passive: true })
      }
      activityInterval = setInterval(() => {
        if (Date.now() - lastActivityAt >= INACTIVITY_TIMEOUT_MS) {
          this.clear()
          notifyInactivityTimeout()
        }
      }, ACTIVITY_CHECK_INTERVAL_MS)
    },
    async refreshSession() {
      if (!getToken() || refreshInFlight) return
      const currentToken = getToken()
      refreshInFlight = api('/auth/refresh', { method: 'POST' })
        .then((data) => {
          if (getToken() === currentToken) {
            setToken(data.access_token)
            lastTokenRefreshAt = Date.now()
          }
        })
        .finally(() => {
          refreshInFlight = null
        })
      return refreshInFlight
    },
    clear() {
      stopActivityTracking()
      setToken(null)
      this.user = null
    },
    logout() {
      this.clear()
    },
  },
})
