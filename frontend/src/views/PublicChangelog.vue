<template>
  <div class="max-w-3xl mx-auto px-4 py-12">
    <!-- Repo header -->
    <div class="text-center mb-12" v-if="data">
      <div class="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full bg-gray-100 text-gray-600 text-xs">
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        {{ data.repo.full_name }}
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Changelog</h1>
      <p class="text-gray-500 text-sm" v-if="data.repo.description">{{ data.repo.description }}</p>
      <div class="mt-4 text-xs text-gray-400">
        Powered by <span class="text-brand-600 font-semibold">LogFast</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Loading changelog...</p>
    </div>

    <!-- Changelogs -->
    <div v-else-if="data && data.changelogs.length" class="space-y-8">
      <div
        v-for="cl in data.changelogs"
        :key="cl.id"
        class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
      >
        <div class="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center gap-3">
          <span v-if="cl.version" class="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded font-mono">{{ cl.version }}</span>
          <span class="text-xs text-gray-400">{{ formatDate(cl.published_at) }}</span>
        </div>
        <div class="p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">{{ cl.title }}</h3>
          <div class="prose prose-sm max-w-none text-gray-700" v-html="renderMarkdown(cl.content)"></div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="!loading" class="text-center py-20 text-gray-500">
      <p class="text-4xl mb-4">📝</p>
      <p class="font-medium text-gray-700 mb-1">No changelogs published yet</p>
      <p class="text-sm">Check back soon for updates!</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="text-center py-20">
      <p class="text-4xl mb-4">🔍</p>
      <p class="font-medium text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { renderMarkdown } from '../utils/markdown'

const route = useRoute()
const data = ref(null)
const loading = ref(true)
const error = ref(null)

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

onMounted(async () => {
  try {
    const fullName = `${route.params.owner}/${route.params.repo}`
    const { data: resp } = await axios.get(`${API}/api/public/${fullName}`)
    data.value = resp
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load changelog'
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>
