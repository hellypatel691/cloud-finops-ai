export default function ProviderBreakdown({ providers = [] }) {
  const max = Math.max(...providers.map(p => p.value), 1)

  const colors = {
    AWS:   { bar: '#f59e0b', bg: 'bg-warning/10',  text: 'text-warning' },
    Azure: { bar: '#38bdf8', bg: 'bg-info/10',     text: 'text-info' },
    GCP:   { bar: '#4ade80', bg: 'bg-success/10',  text: 'text-success' },
  }

  return (
    <div className="card p-5 flex flex-col gap-4">
      <span className="text-sm font-semibold text-primary">Provider Breakdown</span>

      <div className="flex flex-col gap-3">
        {providers.map((p, i) => {
          const c = colors[p.name] ?? { bar: '#7B6EF6', bg: 'bg-accent/10', text: 'text-accent-light' }
          const pct = Math.round((p.value / max) * 100)
          return (
            <div key={i} className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${c.bg} ${c.text}`}>
                    {p.name}
                  </span>
                </div>
                <span className="text-xs font-semibold text-primary">
                  ${Number(p.value).toLocaleString()}
                </span>
              </div>
              <div className="h-1.5 bg-border rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${pct}%`, background: c.bar }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
