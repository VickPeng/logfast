/**
 * Shared API configuration.
 * All API calls should use this base URL.
 */
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const API = `${API_BASE}/api`
