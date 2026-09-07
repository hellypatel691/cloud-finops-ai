import Badge from '../ui/Badge'

const PROVIDER_VARIANT = { AWS: 'warning', Azure: 'info', GCP: 'success' }

function DimensionRow({ item }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
      <div className="flex items-center gap-2">
        <span className="text-xs text-primary font-medium">{item.value}</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-24 h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full"
            style={{ width: `${Math.min(item.pct, 100)}%` }}
          />
        </div>
        <span className="text-[11px] text-secondary w-8 text-right">{item.pct.toFixed(0)}%</span>
        <span className="text-xs font-semibold text-primary font-mono w-20 text-right">
          ${item.cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </span>
      </div>
    </div>
  )
}

export default function RootCausePanel({ rootCause, loading }) {
  if (loading) {
    return (
      <div className="card p-5 flex flex-col gap-4">
        <span className="text-sm font-semibold text-primary">Root Cause Attribution</span>
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-8 bg-border animate-pulse rounded-xl" />
        ))}
      </div>
    )
  }

  if (!rootCause || rootCause.total_anomaly_count === 0) return null

  return (
    <div className="card p-5 flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-primary">Root Cause Attribution</span>
        <Badge variant="danger">
          {rootCause.total_anomaly_count} anomalies · ${rootCause.total_anomaly_cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </Badge>
      </div>

      {/* AI Summary */}
      {rootCause.summary && (
        <div className="bg-bg rounded-xl p-3 border border-accent/20">
          <p className="text-xs text-secondary leading-relaxed">{rootCause.summary}</p>
        </div>
      )}

      {/* Dimensions grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* By Service */}
        {rootCause.by_service?.length > 0 && (
          <div>
            <span className="label mb-2 block">By Service</span>
            {rootCause.by_service.slice(0, 5).map((item, i) => (
              <DimensionRow key={i} item={item} />
            ))}
          </div>
        )}

        {/* By Environment */}
        {rootCause.by_environment?.length > 0 && (
          <div>
            <span className="label mb-2 block">By Environment</span>
            {rootCause.by_environment.slice(0, 5).map((item, i) => (
              <DimensionRow key={i} item={item} />
            ))}
          </div>
        )}

        {/* By Provider */}
        {rootCause.by_provider?.length > 0 && (
          <div>
            <span className="label mb-2 block">By Provider</span>
            {rootCause.by_provider.map((item, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                <Badge variant={PROVIDER_VARIANT[item.value] ?? 'muted'}>{item.value}</Badge>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-secondary">{item.pct.toFixed(0)}%</span>
                  <span className="text-xs font-semibold text-primary font-mono">
                    ${item.cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* By Region */}
        {rootCause.by_region?.length > 0 && (
          <div>
            <span className="label mb-2 block">By Region</span>
            {rootCause.by_region.slice(0, 5).map((item, i) => (
              <DimensionRow key={i} item={item} />
            ))}
          </div>
        )}
      </div>

      {/* Top anomaly chains */}
      {rootCause.top_anomaly_chain?.length > 0 && (
        <div className="flex flex-col gap-2 border-t border-border pt-4">
          <span className="text-xs font-semibold text-primary">Highest-Impact Combinations</span>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  {['Service', 'Environment', 'Region', 'Provider', 'Count', 'Cost'].map(h => (
                    <th key={h} className="px-3 py-2 text-left text-[11px] text-secondary font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rootCause.top_anomaly_chain.slice(0, 8).map((chain, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-border/10">
                    <td className="px-3 py-2 text-primary font-medium">{chain.service ?? '—'}</td>
                    <td className="px-3 py-2 text-secondary">{chain.environment ?? '—'}</td>
                    <td className="px-3 py-2 text-secondary">{chain.region ?? '—'}</td>
                    <td className="px-3 py-2">
                      <Badge variant={PROVIDER_VARIANT[chain.cloud_provider] ?? 'muted'}>
                        {chain.cloud_provider ?? '—'}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-secondary">{chain.count}</td>
                    <td className="px-3 py-2 text-danger font-semibold font-mono">
                      ${chain.cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
