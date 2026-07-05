<template>
  <div class="min-h-screen bg-white">
    <nav class="border-b border-gray-200 bg-white/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-2 font-bold text-lg">
          <span class="text-brand-500">⚡</span>
          <span class="gradient-text">LogFast</span>
        </router-link>
        <div class="flex items-center gap-4">
          <template v-if="auth.authLoading">
            <div class="flex items-center gap-2 text-sm text-gray-400">
              <div class="animate-spin w-3.5 h-3.5 border-2 border-gray-300 border-t-gray-600 rounded-full"></div>
              <span>Loading...</span>
            </div>
          </template>
          <template v-else-if="auth.user">
            <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-gray-900 transition">Dashboard</router-link>
            <div class="flex items-center gap-2">
              <img v-if="auth.user.github_avatar" :src="auth.user.github_avatar" class="w-7 h-7 rounded-full ring-1 ring-gray-300" />
              <span class="text-sm text-gray-700">{{ auth.user.github_login }}</span>
              <button @click="handleLogout" class="text-xs text-gray-400 hover:text-red-500 ml-1 transition">Sign out</button>
            </div>
          </template>
          <template v-else>
            <a :href="API_BASE + '/api/auth/login'" class="bg-gray-900 hover:bg-gray-800 text-white text-sm px-4 py-2 rounded-lg transition flex items-center gap-2">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              Sign in with GitHub
            </a>
          </template>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/')
}

onMounted(async () => {
  await auth.initSession()
})
</script>
