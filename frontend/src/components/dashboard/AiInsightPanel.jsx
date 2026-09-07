import { Sparkles, Send } from 'lucide-react'
import { useState } from 'react'
import Badge from '../ui/Badge'

export default function AiInsightPanel({ summary, stats }) {
  const [input, setInput] = useState('')

  return (
    <div className="card p-5 flex flex-col gap-4 h-full">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Sparkles size={14} className="text-accent" />
        <span className="text-sm font-semibold text-primary">How can I help you?</span>
      </div>

      {/* AI Summary */}
      <div>
        <p className="text-xs font-semibold text-primary mb-1.5">AI Summary</p>
        <p className="text-xs text-secondary leading-relaxed line-clamp-4">
          {summary ?? 'Upload billing data to generate AI-powered cost insights and anomaly explanations.'}
        </p>
      </div>

      {/* Mini stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-3">
          {stats.map((s, i) => (
            <div key={i} className="bg-bg rounded-xl p-3 flex flex-col gap-1.5">
              <span className="text-[10px] text-secondary">{s.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-primary">{s.value}</span>
                <Badge variant={s.badgeVariant}>{s.badge}</Badge>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ask input */}
      <div className="mt-auto flex items-center gap-2 bg-bg border border-border rounded-xl px-3 py-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          className="flex-1 bg-transparent text-xs text-primary placeholder-muted outline-none"
        />
        <button
          className="w-6 h-6 rounded-lg bg-accent flex items-center justify-center text-white hover:bg-accent-light transition-colors"
          onClick={() => setInput('')}
        >
          <Send size={11} />
        </button>
      </div>
    </div>
  )
}
