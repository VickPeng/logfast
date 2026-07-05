import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'
import { API } from '../api'

export const useRepoStore = defineStore('repos', {
  state: () => ({
    allRepos: [],
    connectedRepos: [],
    changelogs: {},
    loading: false,
    connectingRepoId: null, // tracks which repo is being connected
    disconnectingRepoId: null, // tracks which repo is being disconnected
    error: null,
    _connectedFetched: false, // cache flag to avoid refetch
  }),

  actions: {
    async fetchAllRepos() {
      const auth = useAuthStore()
      const { data } = await axios.get(`${API}/repos`, auth.authHeader)
      this.allRepos = data
      return data
    },

    async fetchConnectedRepos(force = false) {
      // Skip if already fetched (unless forced)
      if (this._connectedFetched && !force) return this.connectedRepos

      const auth = useAuthStore()
      const { data } = await axios.get(`${API}/repos/connected`, auth.authHeader)
      this.connectedRepos = data
      this._connectedFetched = true
      return data
    },

    async connectRepo(repo) {
      const auth = useAuthStore()
      this.connectingRepoId = repo.github_id
      this.error = null
      try {
        const { data } = await axios.post(`${API}/repos/connect`, {
          github_repo_id: repo.github_id,
          full_name: repo.full_name,
          name: repo.name,
          description: repo.description,
          private: repo.private,
        }, auth.authHeader)
        await this.fetchAllRepos()
        // Also try to refresh connected repos (non-blocking)
        try { await this.fetchConnectedRepos(true) } catch {}
        return data
      } catch (e) {
        this.error = e.response?.data?.detail || 'Failed to connect repository'
        throw e
      } finally {
        this.connectingRepoId = null
      }
    },

    async disconnectRepo(repoId) {
      const auth = useAuthStore()
      this.error = null
      this.disconnectingRepoId = repoId
      try {
        await axios.post(`${API}/repos/${repoId}/disconnect`, {}, auth.authHeader)
        await this.fetchAllRepos()
        try { await this.fetchConnectedRepos(true) } catch {}
      } catch (e) {
        this.error = e.response?.data?.detail || 'Failed to disconnect repository'
        throw e
      } finally {
        this.disconnectingRepoId = null
      }
    },

    async fetchChangelogs(repoId) {
      const auth = useAuthStore()
      const { data } = await axios.get(`${API}/changelogs/${repoId}`, auth.authHeader)
      this.changelogs[repoId] = data
      return data
    },

    async generateChangelog(repoId, since = null) {
      const auth = useAuthStore()
      const payload = { repo_id: repoId }
      if (since) payload.since = since
      const { data } = await axios.post(`${API}/changelogs/generate`, payload, auth.authHeader)
      await this.fetchChangelogs(repoId)
      return data
    },

    async publishChangelog(changelogId) {
      const auth = useAuthStore()
      await axios.post(`${API}/changelogs/${changelogId}/publish`, {}, auth.authHeader)
    },

    async updateChangelog(changelogId, data) {
      const auth = useAuthStore()
      const resp = await axios.patch(`${API}/changelogs/${changelogId}/edit`, data, auth.authHeader)
      return resp.data
    },
  },
})
