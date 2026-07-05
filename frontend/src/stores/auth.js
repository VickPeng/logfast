import { defineStore } from 'pinia'
import axios from 'axios'
import { API } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    loading: false,
    authLoading: true, // true during initial session restore
    sessionReady: false, // true after initial session check completes
  }),

  getters: {
    authHeader(state) {
      return state.token ? { params: { github_token: state.token } } : {}
    },

    isAuthenticated(state) {
      return !!state.token
    },
  },

  actions: {
    setSession(token, userId) {
      this.token = token
      localStorage.setItem('github_token', token)
      localStorage.setItem('user_id', userId)
    },

    loadSession() {
      const token = localStorage.getItem('github_token')
      const userJson = localStorage.getItem('user')
      if (token) {
        this.token = token
      }
      if (userJson) {
        try {
          this.user = JSON.parse(userJson)
        } catch {
          // ignore invalid JSON
        }
      }
    },

    /**
     * Initialize session on app boot — loads token from storage,
     * verifies it's still valid, and sets sessionReady.
     * Call once at app startup before resolving protected routes.
     */
    async initSession() {
      // Prevent double initialization
      if (this.sessionReady) return
      this.authLoading = true
      this.loadSession()

      if (this.token) {
        try {
          await this.fetchUser()
        } catch {
          // fetchUser already calls logout() on error
        }
      }

      this.sessionReady = true
      this.authLoading = false
    },

    async fetchUser() {
      if (!this.token) return
      this.loading = true
      try {
        const { data } = await axios.get(`${API}/auth/me`, {
          params: { github_token: this.token },
        })
        this.user = data
        // Cache user in localStorage for instant restore on refresh
        localStorage.setItem('user', JSON.stringify(data))
      } catch (e) {
        this.logout()
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('github_token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('user')
    },
  },
})
