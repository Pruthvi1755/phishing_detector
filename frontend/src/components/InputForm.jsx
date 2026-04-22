/**
 * InputForm.jsx — URL input with client-side validation.
 */
import { useState } from 'react'

export default function InputForm({ onSubmit, loading }) {
  const [url, setUrl]     = useState('')
  const [error, setError] = useState('')

  function validate(value) {
    if (!value.trim()) return 'Please enter a URL.'
    if (!/^https?:\/\//i.test(value.trim()))
      return 'URL must start with http:// or https://'
    if (value.length > 2048) return 'URL is too long (max 2048 chars).'
    if (/\s/.test(value))    return 'URL must not contain spaces.'
    return ''
  }

  function handleSubmit(e) {
    e.preventDefault()
    const err = validate(url)
    if (err) { setError(err); return }
    setError('')
    onSubmit(url.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4" noValidate>
      <div className="relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#00ff88]/40 select-none pointer-events-none">
          🔍
        </span>
        <input
          type="url"
          value={url}
          onChange={e => { setUrl(e.target.value); setError('') }}
          placeholder="https://example.com"
          disabled={loading}
          autoFocus
          className={[
            'w-full pl-11 pr-4 py-4 rounded-lg font-mono text-sm',
            'bg-[#0a0f1e] border text-white placeholder-white/20',
            'focus:outline-none focus:ring-2 focus:ring-[#00ff88]/30',
            'transition-all duration-200',
            error
              ? 'border-[#ff3b5c]/50'
              : 'border-[#00ff88]/20 hover:border-[#00ff88]/40',
            loading ? 'opacity-40 cursor-not-allowed' : '',
          ].join(' ')}
          aria-label="URL to analyse"
          aria-describedby={error ? 'url-error' : undefined}
        />
      </div>

      {error && (
        <p id="url-error" className="text-[#ff3b5c] text-xs font-mono pl-1 animate-fadeUp" role="alert">
          ⚠ {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading || !url.trim()}
        className={[
          'w-full py-4 rounded-lg font-display font-semibold text-sm tracking-widest uppercase',
          'transition-all duration-300 select-none',
          loading || !url.trim()
            ? 'bg-[#00ff88]/8 text-[#00ff88]/25 cursor-not-allowed border border-[#00ff88]/10'
            : 'bg-[#00ff88] text-[#020817] hover:bg-[#00e07a] glow-green cursor-pointer active:scale-[0.98]',
        ].join(' ')}
      >
        {loading ? 'Scanning…' : 'Analyse URL'}
      </button>
    </form>
  )
}
