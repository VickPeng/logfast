<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-sm text-gray-500 mt-0.5">Manage your changelogs</p>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
      <div class="flex items-center justify-between">
        <p class="text-sm text-red-600">{{ error }}</p>
        <button @click="retry" class="text-xs bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1 rounded transition">Retry</button>
      </div>
    </div>

    <!-- Connected Repos -->
    <section v-if="connectedFromAllRepos.length" class="mb-12">
      <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Connected Repositories</h2>
      <div class="grid gap-3">
        <div
          v-for="repo in connectedFromAllRepos"
          :key="repo.github_id"
          class="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between hover:border-gray-300 transition cursor-pointer shadow-sm"
          @click="$router.push(`/changelog/${repo.connected_repo_id}`)"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">📦</span>
            <div>
              <p class="font-medium text-gray-900">{{ repo.full_name }}</p>
              <p class="text-xs text-gray-500">{{ repo.description || 'No description' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span v-if="repo.private" class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">private</span>
            <span v-else class="text-xs bg-brand-50 text-brand-600 px-2 py-0.5 rounded">public</span>
            <a
              :href="'/p/' + repo.full_name"
              target="_blank"
              class="text-xs text-gray-400 hover:text-brand-600 transition"
              @click.stop
              title="View public changelog page"
            >📝 Changelog</a>
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </div>
        </div>
      </div>
    </section>

    <!-- All repos to connect -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">Your Repositories</h2>
        <div class="flex items-center gap-2">
          <button
            v-for="f in ['all','unconnected','connected']"
            :key="f"
            @click="filter = f"
            :class="filter === f ? 'bg-gray-200 text-gray-900' : 'text-gray-500 hover:text-gray-700'"
            class="text-xs px-2.5 py-1 rounded transition capitalize"
          >{{ f }}</button>
        </div>
      </div>
      <div v-if="store.loading" class="text-center py-10 text-gray-500">Loading repositories...</div>
      <div v-else class="grid gap-3">
        <div
          v-for="repo in filteredRepos"
          :key="repo.github_id"
          class="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between shadow-sm"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">{{ repo.private ? '🔒' : '📦' }}</span>
            <div>
              <p class="font-medium text-gray-900">{{ repo.full_name }}</p>
              <p class="text-xs text-gray-500">
                {{ repo.language || 'Unknown' }}
                <span v-if="repo.stars" class="ml-2">⭐ {{ repo.stars }}</span>
              </p>
            </div>
          </div>
          <div>
            <button
              v-if="!repo.connected"
              :disabled="store.connectingRepoId === repo.github_id"
              @click="handleConnect(repo)"
              class="text-xs bg-brand-50 text-brand-600 border border-brand-200 px-3 py-1.5 rounded-lg hover:bg-brand-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="store.connectingRepoId === repo.github_id" class="flex items-center gap-1">
                <span class="inline-block w-3 h-3 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></span>
                Connecting...
              </span>
              <span v-else>Connect</span>
            </button>
            <button
              v-else
              :disabled="store.disconnectingRepoId === repo.connected_repo_id"
              @click="handleDisconnect(repo.connected_repo_id)"
              class="text-xs border border-gray-300 text-gray-600 px-3 py-1.5 rounded-lg hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="store.disconnectingRepoId === repo.connected_repo_id" class="flex items-center gap-1">
                <span class="inline-block w-3 h-3 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></span>
                Disconnecting...
              </span>
              <span v-else>Disconnect</span>
            </button>
          </div>
        </div>
      </div>
      <div v-if="!store.loading && !store.allRepos.length" class="text-center py-10 text-gray-500">
        No repositories found. Make sure you have GitHub repos.
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRepoStore } from '../stores/repos'
import { useAuthStore } from '../stores/auth'

const store = useRepoStore()
const auth = useAuthStore()
const router = useRouter()
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const error = ref('')
const filter = ref('unconnected')

const filteredRepos = computed(() => {
  if (filter.value === 'connected') return store.allRepos.filter(r => r.connected)
  if (filter.value === 'unconnected') return store.allRepos.filter(r => !r.connected)
  return store.allRepos
})

const connectedFromAllRepos = computed(() =>
  store.allRepos.filter(r => r.connected)
)

onMounted(async () => {
  // Route guard already verified the session — just make sure user data is loaded
  if (!auth.user && auth.token) {
    try {
      await auth.fetchUser()
    } catch (e) {
      auth.logout()
      router.push('/')
      return
    }
  }
  store.loading = true
  try {
    await store.fetchAllRepos()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load repositories. Please try again.'
  }
  store.loading = false
})

async function retry() {
  error.value = ''
  store.loading = true
  try {
    await store.fetchAllRepos()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load repositories.'
  }
  store.loading = false
}

async function handleConnect(repo) {
  try {
    await store.connectRepo(repo)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to connect repository.'
  }
}

async function handleDisconnect(repoId) {
  try {
    await store.disconnectRepo(repoId)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to disconnect repository.'
  }
}
</script>
