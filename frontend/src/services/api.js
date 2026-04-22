/**
 * api.js — All backend communication for PhishGuard.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Send a URL to the backend for phishing analysis.
 * @param {string} url
 * @returns {Promise<{data: Object|null, error: string|null}>}
 */
export async function checkURL(url) {
  try {
    const { data } = await client.post('/predict', { url })
    return { data, error: null }
  } catch (err) {
    const msg =
      err.response?.data?.detail ||
      (err.code === 'ECONNABORTED'
        ? 'Request timed out. Is the backend running on port 8000?'
        : err.message) ||
      'An unexpected error occurred.'
    return { data: null, error: msg }
  }
}

export async function healthCheck() {
  try {
    const { data } = await client.get('/health')
    return data
  } catch {
    return null
  }
}
