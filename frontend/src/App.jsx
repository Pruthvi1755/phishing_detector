/**
 * App.jsx — Root component.
 * Manages dark/light mode, API call orchestration, and page layout.
 */
import { useState, useEffect } from 'react'
import InputForm  from './components/InputForm.jsx'
import ResultCard from './components/ResultCard.jsx'
import Loader     from './components/Loader.jsx'
import { checkURL } from './services/api.js'

export default function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState(null)
  const [apiError, setApiError] = useState('')

  // Sync dark class on <html>
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  async function handleSubmit(url) {
    setLoading(true)
    setResult(null)
    setApiError('')

    const { data, error } = await checkURL(url)

    setLoading(false)
    if (error) setApiError(error)
    else        setResult(data)
  }

  function handleReset() {
    setResult(null)
    setApiError('')
  }

  const showHero = !result && !loading && !apiError

  return (
    <div className="min-h-screen bg-[#020817] text-white relative overflow-x-hidden">

      {/* Scanline overlay */}
      <div className="scanline" aria-hidden="true" />

      {/* Ambient glow blobs */}
      <div className="fixed top-[-10%] left-[20%] w-[500px] h-[500px] bg-[#00ff88]/[0.025] rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-[-5%] right-[15%] w-[400px] h-[400px] bg-[#1a0df0]/[0.04] rounded-full blur-3xl pointer-events-none" />

      {/* ── Navigation ── */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/[0.05]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#00ff88]/10 border border-[#00ff88]/25 flex items-center justify-center">
            <span className="text-[#00ff88] text-sm leading-none">⚡</span>
          </div>
          <span className="font-display font-bold text-lg tracking-tight">
            Phish<span className="text-[#00ff88]">Guard</span>
          </span>
          <span className="hidden sm:inline font-mono text-[9px] text-white/20 border border-white/10 px-2 py-0.5 rounded-full tracking-widest">
            AI POWERED
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="hidden sm:flex items-center gap-1.5 font-mono text-[10px] text-[#00ff88]/50">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00ff88] animate-pulse" />
            ONLINE
          </span>
          <button
            onClick={() => setDarkMode(d => !d)}
            className="w-9 h-9 rounded-lg border border-white/10 flex items-center justify-center
                       text-white/40 hover:text-white hover:border-white/25 transition-all duration-200"
            aria-label="Toggle dark/light mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </nav>

      {/* ── Main Content ── */}
      <main className="relative z-10 flex flex-col items-center px-4 py-12 sm:py-16">
        <div className="w-full max-w-lg space-y-8">

          {/* Hero section */}
          {showHero && (
            <div className="text-center space-y-4 animate-fadeUp">
              <div className="inline-flex items-center gap-2 font-mono text-[9px] text-[#00ff88]/50
                              border border-[#00ff88]/15 rounded-full px-3 py-1.5 tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00ff88] animate-pulse" />
                MODEL LOADED — 90.76% ACCURACY
              </div>

              <h1 className="font-display font-bold text-4xl sm:text-5xl leading-tight tracking-tight">
                Detect Phishing<br />
                <span className="shimmer-text">Instantly.</span>
              </h1>

              <p className="text-white/35 text-sm leading-relaxed max-w-xs mx-auto">
                Paste any URL. Our AI scans for phishing indicators,
                suspicious patterns, and security threats in milliseconds.
              </p>
            </div>
          )}

          {/* Terminal card */}
          <div className="terminal-border p-6">

            {/* Window chrome dots */}
            {!loading && !result && (
              <div className="flex items-center gap-1.5 pb-5 border-b border-white/[0.05] mb-5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ff3b5c]/60" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#ffb347]/60" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#00ff88]/60" />
                <span className="ml-2 font-mono text-[9px] text-white/15 tracking-wider">
                  phishguard://scan
                </span>
              </div>
            )}

            {loading  && <Loader />}
            {!loading && result && <ResultCard result={result} onReset={handleReset} />}
            {!loading && !result && <InputForm onSubmit={handleSubmit} loading={loading} />}

            {/* API-level error */}
            {apiError && !loading && (
              <div className="mt-4 p-4 rounded-lg animate-fadeUp"
                   style={{ background: 'rgba(255,59,92,0.08)', border: '1px solid rgba(255,59,92,0.25)' }}>
                <p className="text-[#ff3b5c] text-sm font-mono leading-relaxed">⚠ {apiError}</p>
                <button
                  onClick={handleReset}
                  className="text-[10px] text-white/30 hover:text-white/60 mt-2 transition-colors font-mono"
                >
                  ← Try again
                </button>
              </div>
            )}
          </div>

          {/* Feature tags */}
          {showHero && (
            <div className="flex flex-wrap justify-center gap-2 animate-fadeUp">
              {['ML-Powered', '13 URL Features', 'Real-time', 'GradientBoosting', 'Open Source'].map(tag => (
                <span key={tag}
                  className="font-mono text-[9px] text-white/25 border border-white/8 rounded-full px-3 py-1 tracking-wider">
                  {tag}
                </span>
              ))}
            </div>
          )}

        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 text-center pb-8">
        <p className="font-mono text-[9px] text-white/15 tracking-widest">
          PHISHGUARD v1.0 — FINAL YEAR PROJECT — AI PHISHING DETECTION SYSTEM
        </p>
      </footer>
    </div>
  )
}
