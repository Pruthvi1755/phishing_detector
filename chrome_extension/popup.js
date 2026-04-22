/**
 * popup.js — PhishGuard Chrome Extension
 * Gets the current tab URL and calls the PhishGuard backend API.
 */

const API_BASE = 'http://localhost:8000'

const STATUS_EMOJI = { SAFE: '✅', SUSPICIOUS: '⚠️', PHISHING: '🚨' }

const urlText   = document.getElementById('url-text')
const scanBtn   = document.getElementById('scan-btn')
const resultEl  = document.getElementById('result')
const errorBox  = document.getElementById('error-box')
const badge     = document.getElementById('status-badge')

let currentUrl = ''

// ── Load current tab URL ─────────────────────────────────────────────────────
chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  if (!tab?.url) {
    urlText.textContent = 'Could not read page URL.'
    scanBtn.disabled = true
    return
  }
  currentUrl = tab.url
  urlText.textContent = currentUrl
})

// ── Scan button ──────────────────────────────────────────────────────────────
scanBtn.addEventListener('click', async () => {
  if (!currentUrl) return

  // Reset UI
  resultEl.style.display = 'none'
  resultEl.className = ''
  errorBox.style.display = 'none'
  scanBtn.disabled = true
  scanBtn.textContent = 'Scanning…'
  badge.textContent = 'SCANNING'

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: currentUrl }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    showResult(data)
  } catch (err) {
    showError(
      err.message.includes('fetch')
        ? '⚠ Backend unreachable. Start the server:\n  uvicorn backend.main:app --reload'
        : `⚠ ${err.message}`
    )
  } finally {
    scanBtn.disabled = false
    scanBtn.textContent = '🔍 Scan This Page'
  }
})

// ── Render result ─────────────────────────────────────────────────────────────
function showResult(data) {
  const score = Math.round(data.risk_score)

  resultEl.className = data.status
  resultEl.style.display = 'block'

  document.getElementById('result-emoji').textContent    = STATUS_EMOJI[data.status] ?? '❓'
  document.getElementById('result-status').textContent   = data.status
  document.getElementById('result-score').textContent    = `${score}% risk`
  document.getElementById('result-explanation').textContent =
    data.explanations?.[0] ?? 'No explanation available.'

  // Animate bar
  const bar = document.getElementById('result-bar')
  bar.style.width = '0%'
  setTimeout(() => { bar.style.width = `${score}%` }, 50)

  badge.textContent = data.status
}

// ── Render error ──────────────────────────────────────────────────────────────
function showError(msg) {
  errorBox.textContent = msg
  errorBox.style.display = 'block'
  badge.textContent = 'ERROR'
}
