/**
 * api.js — All backend communication for PhishGuard.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 45000, // Increased to 45s for Render cold starts
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
    let msg = err.response?.data?.detail || err.message || 'An unexpected error occurred.'
    
    if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
      msg = 'Request timed out. The server might be waking up from sleep. Please try again in 30 seconds.'
    } else if (err.code === 'ERR_NETWORK') {
      msg = 'Cannot connect to backend. Check if VITE_API_URL is set correctly in Vercel.'
    }
    
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
