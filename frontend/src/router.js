import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('./views/LandingPage.vue'),
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('./views/AuthCallback.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('./views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/changelog/:repoId',
    name: 'changelog',
    component: () => import('./views/ChangelogPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/p/:owner/:repo',
    name: 'public-changelog',
    component: () => import('./views/PublicChangelog.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('./views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Route guard — redirect to landing if not authenticated
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()

    // If session hasn't been initialized yet (e.g. page refresh), wait for it
    if (!auth.sessionReady) {
      await auth.initSession()
    }

    if (!auth.token) {
      next({ name: 'landing' })
      return
    }
  }
  next()
})

export default router
