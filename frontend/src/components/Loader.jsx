/**
 * Loader.jsx — Animated scanning indicator shown during API call.
 */
export default function Loader() {
  const lines = ['Resolving domain...', 'Extracting features...', 'Running AI model...']

  return (
    <div className="flex flex-col items-center gap-6 py-10 animate-fadeUp">
      {/* Radar ring */}
      <div className="relative w-24 h-24">
        <div className="absolute inset-0 rounded-full border-2 border-[#00ff88]/10" />
        <div className="absolute inset-2 rounded-full border-2 border-[#00ff88]/20" />
        <div className="absolute inset-4 rounded-full border-2 border-[#00ff88]/40" />
        <div
          className="absolute inset-0 rounded-full border-t-2 border-[#00ff88]"
          style={{ animation: 'spin 1s linear infinite' }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-[#00ff88] text-[10px] font-mono tracking-widest">SCAN</span>
        </div>
      </div>

      {/* Status lines */}
      <div className="font-mono text-xs text-[#00ff88]/70 space-y-1.5 text-left w-48">
        {lines.map((line, i) => (
          <p
            key={line}
            style={{ animation: `fadeUp 0.4s ease ${i * 0.25}s both` }}
          >
            <span className="text-[#00ff88]/30">{'> '}</span>{line}
          </p>
        ))}
      </div>
    </div>
  )
}
