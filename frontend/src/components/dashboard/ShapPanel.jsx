import { Sparkles } from 'lucide-react'
import Badge from '../ui/Badge'

function DirectionDot({ direction }) {
  const colors = {
    increases_risk:  'bg-danger',
    decreases_risk:  'bg-success',
    neutral:         'bg-muted',
  }
  return <span className={`w-1.5 h-1.5 rounded-full inline-block ${colors[direction] ?? 'bg-muted'}`} />
}

export default function ShapPanel({ globalImportance = [], recordExplanations = [], loading }) {
  if (loading) {
    return (
      <div className="card p-5 flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-accent" />
          <span className="text-sm font-semibold text-primary">SHAP Feature Importance</span>
        </div>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="h-2.5 w-32 bg-border animate-pulse rounded" />
            <div className="flex-1 h-2 bg-border animate-pulse rounded-full" />
            <div className="h-2.5 w-8 bg-border animate-pulse rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (!globalImportance.length) return null

  const maxImp = Math.max(...globalImportance.map(f => f.importance), 1)

  return (
    <div className="card p-5 flex flex-col gap-5">
      {/* Global importance */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles size={14} className="text-accent" />
            <span className="text-sm font-semibold text-primary">SHAP Feature Importance</span>
          </div>
          <span className="text-xs text-secondary">mean |SHAP| across anomalies</span>
        </div>

        <div className="flex flex-col gap-2.5">
          {globalImportance.slice(0, 8).map((f, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 w-48 shrink-0">
                <DirectionDot direction={f.direction} />
                <span className="text-xs text-secondary font-mono truncate">{f.feature}</span>
              </div>
              <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    f.direction === 'increases_risk' ? 'bg-danger' :
                    f.direction === 'decreases_risk' ? 'bg-success' : 'bg-accent'
                  }`}
                  style={{ width: `${(f.importance / maxImp) * 100}%` }}
                />
              </div>
              <span className="text-[11px] text-secondary font-mono w-10 text-right">
                {f.importance.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-[11px] text-secondary pt-1">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-danger inline-block" /> Increases risk</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-success inline-block" /> Decreases risk</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-accent inline-block" /> Neutral</span>
        </div>
      </div>

      {/* Top record explanations */}
      {recordExplanations.length > 0 && (
        <div className="flex flex-col gap-3 border-t border-border pt-4">
          <span className="text-xs font-semibold text-primary">Top Anomaly Explanations</span>
          <div className="flex flex-col gap-3">
            {recordExplanations.slice(0, 5).map((rec, i) => (
              <div key={i} className="bg-bg rounded-xl p-3 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-primary">
                    {rec.service} · {rec.cloud_provider}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-secondary">{rec.date}</span>
                    <span className="text-xs font-semibold text-danger">
                      ${rec.total_cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-secondary leading-relaxed">{rec.top_reason}</p>
                {/* Mini contribution bars */}
                <div className="flex flex-col gap-1 mt-1">
                  {rec.feature_contributions.slice(0, 4).map((c, j) => (
                    <div key={j} className="flex items-center gap-2">
                      <span className="text-[10px] text-muted font-mono w-36 truncate">{c.feature}</span>
                      <div className="flex-1 h-1 bg-border rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${c.shap_value > 0 ? 'bg-danger/60' : 'bg-success/60'}`}
                          style={{ width: `${Math.min(Math.abs(c.shap_value) * 200, 100)}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-muted font-mono w-12 text-right">
                        {c.shap_value > 0 ? '+' : ''}{c.shap_value.toFixed(3)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
