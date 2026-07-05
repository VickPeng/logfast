<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-gray-700 mb-1 inline-block">← Dashboard</router-link>
        <h1 class="text-xl font-bold text-gray-900" v-if="repo">{{ repo.full_name }}</h1>
      </div>
      <button
        @click="handleGenerate"
        :disabled="generating"
        class="bg-gray-900 hover:bg-gray-800 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition flex items-center gap-2 shadow-sm"
      >
        <svg v-if="generating" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        <span v-else>🤖</span>
        {{ generating ? 'Generating...' : 'Generate Changelog' }}
      </button>
    </div>

    <!-- Changelog list -->
    <div v-if="changelogs.length" class="space-y-4">
      <div
        v-for="cl in changelogs"
        :key="cl.id"
        class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
      >
        <div class="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span v-if="cl.version" class="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded font-mono">{{ cl.version }}</span>
            <span
              :class="cl.status === 'published' ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'"
              class="text-xs px-2 py-0.5 rounded"
            >
              {{ cl.status }}
            </span>
            <span class="text-xs text-gray-400">{{ formatDate(cl.created_at) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="cl.status === 'draft' && editingId !== cl.id"
              @click="startEdit(cl)"
              class="text-xs bg-gray-100 text-gray-600 border border-gray-200 px-3 py-1 rounded-lg hover:bg-gray-200 transition"
            >Edit</button>
            <button
              v-if="cl.status === 'draft' && editingId !== cl.id"
              @click="handlePublish(cl.id)"
              :disabled="publishing === cl.id"
              class="text-xs bg-brand-50 text-brand-600 border border-brand-200 px-3 py-1 rounded-lg hover:bg-brand-100 disabled:opacity-50 transition flex items-center gap-1.5"
            >
              <svg v-if="publishing === cl.id" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              {{ publishing === cl.id ? 'Publishing...' : 'Publish' }}
            </button>
            <template v-if="editingId === cl.id">
              <button @click="saveEdit(cl.id)" :disabled="saving" class="text-xs bg-gray-900 text-white px-3 py-1 rounded-lg hover:bg-gray-800 disabled:opacity-50 transition flex items-center gap-1.5">
                <svg v-if="saving" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
              <button @click="cancelEdit()" :disabled="saving" class="text-xs border border-gray-300 text-gray-600 px-3 py-1 rounded-lg hover:bg-gray-100 disabled:opacity-50 transition">Cancel</button>
            </template>
          </div>
        </div>
        <div class="p-6" v-if="editingId !== cl.id">
          <h3 class="text-lg font-bold text-gray-900 mb-4">{{ cl.title }}</h3>
          <div class="prose prose-sm max-w-none text-gray-700" v-html="renderMarkdown(cl.content)"></div>
        </div>
        <!-- Edit form -->
        <div class="p-6" v-else>
          <label class="text-xs font-medium text-gray-500 mb-1 block">Title</label>
          <input v-model="editTitle" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400" />
          <label class="text-xs font-medium text-gray-500 mb-1 block">Content (Markdown)</label>
          <textarea v-model="editContent" rows="12" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-400" />
        </div>
      </div>
    </div>

    <div v-else-if="!generating" class="text-center py-20 text-gray-500">
      <p class="text-4xl mb-4">📝</p>
      <p class="font-medium text-gray-700 mb-1">No changelogs yet</p>
      <p class="text-sm">Click "Generate Changelog" to create your first one.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRepoStore } from '../stores/repos'
import { renderMarkdown } from '../utils/markdown'

const route = useRoute()
const store = useRepoStore()
const generating = ref(false)
const saving = ref(false)
const publishing = ref(null) // tracks which changelog id is being published
const editingId = ref(null)
const editTitle = ref('')
const editContent = ref('')

const repo = computed(() => {
  return store.allRepos.filter(r => r.connected).find(r => r.connected_repo_id === parseInt(route.params.repoId))
})

const changelogs = computed(() => {
  return store.changelogs[route.params.repoId] || []
})

onMounted(async () => {
  await store.fetchAllRepos()
  await store.fetchChangelogs(route.params.repoId)
})

function startEdit(cl) {
  editingId.value = cl.id
  editTitle.value = cl.title
  editContent.value = cl.content
}

function cancelEdit() {
  editingId.value = null
  editTitle.value = ''
  editContent.value = ''
}

async function saveEdit(changelogId) {
  saving.value = true
  try {
    await store.updateChangelog(changelogId, {
      title: editTitle.value,
      content: editContent.value,
    })
    await store.fetchChangelogs(route.params.repoId)
    cancelEdit()
  } finally {
    saving.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  await store.generateChangelog(parseInt(route.params.repoId))
  generating.value = false
}

async function handlePublish(changelogId) {
  publishing.value = changelogId
  try {
    await store.publishChangelog(changelogId)
    await store.fetchChangelogs(route.params.repoId)
  } finally {
    publishing.value = null
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  // Backend returns UTC times — ensure they're treated as UTC, not local
  const d = new Date(dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z')
  const now = new Date()
  const diff = now - d
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
