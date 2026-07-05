<template>
  <div class="max-w-lg mx-auto px-4 pt-32 text-center">
    <div class="animate-spin w-10 h-10 border-2 border-brand-400 border-t-transparent rounded-full mx-auto mb-6"></div>
    <h1 class="text-xl font-bold mb-2">Signing you in...</h1>
    <p class="text-sm text-gray-400">Just a moment while we connect your GitHub account.</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  const token = route.query.token
  const userId = route.query.user_id

  if (token) {
    auth.setSession(token, userId)
    await auth.fetchUser()
    router.push('/dashboard')
  } else {
    router.push('/')
  }
})
</script>
