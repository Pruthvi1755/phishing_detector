/**
 * ResultCard.jsx — Displays the phishing analysis result with
 * risk score bar, status badge, explanations, and feature breakdown.
 */

const STATUS_CONFIG = {
  SAFE: {
    color: '#00ff88',
    bg: 'rgba(0,255,136,0.07)',
    border: 'rgba(0,255,136,0.3)',
    glow: 'glow-green',
    emoji: '✅',
    label: 'SAFE',
    desc: 'This URL appears legitimate.',
  },
  SUSPICIOUS: {
    color: '#ffb347',
    bg: 'rgba(255,179,71,0.07)',
    border: 'rgba(255,179,71,0.3)',
    glow: 'glow-amber',
    emoji: '⚠️',
    label: 'SUSPICIOUS',
    desc: 'Proceed with caution.',
  },
  PHISHING: {
    color: '#ff3b5c',
    bg: 'rgba(255,59,92,0.07)',
    border: 'rgba(255,59,92,0.3)',
    glow: 'glow-red',
    emoji: '🚨',
    label: 'PHISHING',
    desc: 'Do NOT visit this website.',
  },
}

const FEATURE_LABELS = {
  url_length:             'URL Length',
  valid_url:              'Valid Structure',
  at_symbol:              '@ Symbol',
  sensitive_words_count:  'Sensitive Words',
  path_length:            'Path Length',
  isHttps:                'HTTPS Enabled',
  nb_dots:                'Dot Count',
  nb_hyphens:             'Hyphen Count',
  nb_and:                 '& Parameters',
  nb_or:                  '| Characters',
  nb_www:                 'WWW Present',
  nb_com:                 '.com Count',
  nb_underscore:          'Underscores',
  url_entropy:            'URL Entropy',
  nb_subdomains:          'Subdomain Count',
  is_ip_address:          'IP Address Host',
  punycode_detected:      'Punycode/Unicode',
  brand_impersonation:    'Brand Impersonation',
  suspicious_tld_score:   'Suspicious TLD',
  random_patterns:        'Random Patterns',
  url_encoding_count:     'Encoded Chars',
}

export default function ResultCard({ result, onReset }) {
  const cfg        = STATUS_CONFIG[result.status] ?? STATUS_CONFIG.SAFE
  const riskScore  = Math.round(result.risk_score)
  const riskyFeats = result.features.filter(f => f.risk)

  return (
    <div className="w-full space-y-4 animate-fadeUp">

      {/* ── Status Header ── */}
      <div
        className="rounded-xl p-5 border flex items-center gap-4"
        style={{ background: cfg.bg, borderColor: cfg.border }}
      >
        <span className="text-4xl leading-none">{cfg.emoji}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h2 className="font-display font-bold text-2xl" style={{ color: cfg.color }}>
              {cfg.label}
            </h2>
            <span
              className="text-[10px] font-mono px-2 py-0.5 rounded-full border"
              style={{ color: cfg.color, borderColor: cfg.border }}
            >
              {result.confidence.toFixed(1)}% confidence
            </span>
          </div>
          <p className="text-white/40 text-xs mt-0.5">{cfg.desc}</p>
          <p className="text-white/25 font-mono text-[10px] mt-1 truncate">
            {result.url}
          </p>
        </div>
      </div>

      {/* ── Risk Score Bar ── */}
      <div className="terminal-border p-5 space-y-3">
        <div className="flex justify-between items-center">
          <span className="font-mono text-[10px] text-white/40 uppercase tracking-widest">Risk Score</span>
          <span className="font-mono font-semibold text-xl" style={{ color: cfg.color }}>
            {riskScore}<span className="text-sm">%</span>
          </span>
        </div>

        <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full progress-bar-fill"
            style={{
              width: `${riskScore}%`,
              background: `linear-gradient(90deg, ${cfg.color}66, ${cfg.color})`,
              boxShadow: `0 0 8px ${cfg.color}80`,
            }}
          />
        </div>

        <div className="flex justify-between font-mono text-[9px] text-white/20 pt-0.5">
          <span>0% — SAFE</span>
          <span>50% — SUSPICIOUS</span>
          <span>100% — PHISHING</span>
        </div>
      </div>

      {/* ── Explanations ── */}
      <div className="terminal-border p-5 space-y-2.5">
        <p className="font-mono text-[10px] text-white/40 uppercase tracking-widest mb-3">
          Analysis Details
        </p>
        {result.explanations.map((exp, i) => (
          <p key={i} className="text-sm text-white/75 leading-relaxed">
            {exp}
          </p>
        ))}
      </div>

      {/* ── Risk Indicators (only if any) ── */}
      {riskyFeats.length > 0 && (
        <div className="terminal-border p-5">
          <p className="font-mono text-[10px] text-white/40 uppercase tracking-widest mb-3">
            Risk Indicators — {riskyFeats.length} flagged
          </p>
          <div className="grid grid-cols-2 gap-2">
            {riskyFeats.map(f => (
              <div
                key={f.name}
                className="flex items-center gap-2 rounded-lg px-3 py-2"
                style={{
                  background: 'rgba(255,59,92,0.05)',
                  border: '1px solid rgba(255,59,92,0.2)',
                }}
              >
                <span className="text-[#ff3b5c] text-[8px]">●</span>
                <span className="text-xs text-white/60 flex-1">{FEATURE_LABELS[f.name] ?? f.name}</span>
                <span className="font-mono text-[10px] text-white/35">{f.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Meta ── */}
      <p className="text-center font-mono text-[9px] text-white/15">
        Analysed in {result.processing_time_ms} ms
      </p>

      {/* ── Reset ── */}
      <button
        onClick={onReset}
        className="w-full py-3 rounded-lg border border-white/8 text-white/40 font-mono text-xs
                   hover:border-[#00ff88]/30 hover:text-[#00ff88]/60
                   transition-all duration-200 active:scale-[0.99]"
      >
        ← Check another URL
      </button>
    </div>
  )
}
