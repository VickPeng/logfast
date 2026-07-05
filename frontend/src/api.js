/**
 * Shared API configuration.
 * All API calls should use this base URL.
 */
// Use VITE_API_URL if set (Vercel Pro), otherwise fall back to same-origin
// so Vercel rewrites can proxy /api/* to the Railway backend.
export const API_BASE = import.meta.env.VITE_API_URL || ''
export const API = `${API_BASE}/api`
