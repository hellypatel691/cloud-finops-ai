import { useState } from 'react'
import { DollarSign, AlertTriangle, TrendingUp, Upload } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getOrganizations } from '../api/organizations'
import { getDashboardSummary } from '../api/auth'
import StatCard from '../components/ui/StatCard'
import SpendBarChart from '../components/charts/SpendBarChart'
import SpendDonutChart from '../components/charts/SpendDonutChart'
import AiInsightPanel from '../components/dashboard/AiInsightPanel'
import RecentAnomalies from '../components/dashboard/RecentAnomalies'
import ProviderBreakdown from '../components/dashboard/ProviderBreakdown'
import ErrorState from '../components/ui/ErrorState'

function Skeleton({ className = '' }) {
  return <div className={`bg-border animate-pulse rounded-xl ${className}`} />
}

const PERIODS = ['Weekly', 'Monthly', 'Yearly']

export default function Dashboard() {
  const [period, setPeriod]       = useState('Monthly')
  const [activeOrgIdx, setActiveOrgIdx] = useState(0)

  const { data: orgs, loading: orgsLoading, error: orgsError } = useApi(getOrganizations)
  const activeOrg = orgs?.[activeOrgIdx]

  const {
    data: summary,
    loading: summaryLoading,
    error: summaryError,
    refetch,
  } = useApi(
    () => activeOrg ? getDashboardSummary(activeOrg.id) : Promise.resolve(null),
    [activeOrg?.id]
  )

  const loading = orgsLoading || summaryLoading
  const error   = orgsError || summaryError

  // ── Chart data from summary ───────────────────────────────────────────────
  const barData = (() => {
    if (!summary?.daily_spend?.length) return []
    // Group by month label for monthly view
    const monthly = {}
    summary.daily_spend.forEach(d => {
      const label = new Date(d.date).toLocaleString('default', { month: 'short' })
      monthly[label] = (monthly[label] ?? 0) + d.total
    })
    return Object.entries(monthly).map(([label, value]) => ({ label, value }))
  })()

  const donutData = (() => {
    if (!summary?.top_services?.length) return { data: [], total: 0 }
    const total = summary.top_services.reduce((s, x) => s + x.total, 0)
    return {
      total,
      data: summary.top_services.map(s => ({
        name:  s.service,
        value: s.total,
        pct:   s.pct.toFixed(1),
      })),
    }
  })()

  const providers = (summary?.provider_breakdown ?? []).map(p => ({
    name:  p.provider,
    value: p.total,
  }))

  const anomalies = (summary?.recent_anomalies ?? []).map(r => ({
    service:  r.service,
    date:     r.date,
    provider: r.cloud_provider,
    cost:     r.total_cost,
  }))

  const activeBarIdx = barData.length - 1

  return (
    <div className="flex flex-col gap-5">

      {/* Org selector */}
      {orgs && orgs.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          {orgs.map((org, i) => (
            <button
              key={org.id}
              onClick={() => setActiveOrgIdx(i)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                i === activeOrgIdx
                  ? 'bg-accent text-white'
                  : 'bg-card border border-border text-secondary hover:text-primary'
              }`}
            >
              {org.name}
            </button>
          ))}
        </div>
      )}

      {error ? (
        <div className="card"><ErrorState error={error} onRetry={refetch} /></div>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28" />)
            ) : (
              <>
                <StatCard
                  title="Total Spend"
                  value={`$${((summary?.total_spend ?? 0) / 1000).toFixed(1)}k`}
                  change={summary?.spend_change_pct ?? 0}
                  changeLabel="vs prev 30 days"
                  icon={DollarSign}
                  accent
                />
                <StatCard
                  title="Anomalies"
                  value={summary?.anomaly_count ?? 0}
                  changeLabel="flagged records"
                  icon={AlertTriangle}
                />
                <StatCard
                  title="Providers"
                  value={providers.length || '—'}
                  changeLabel={providers.map(p => p.name).join(' · ') || 'no data'}
                  icon={TrendingUp}
                />
                <StatCard
                  title="Records"
                  value={(summary?.record_count ?? 0).toLocaleString()}
                  changeLabel={`${summary?.upload_count ?? 0} upload(s) completed`}
                  icon={Upload}
                />
              </>
            )}
          </div>

          {/* Main grid */}
          <div className="grid grid-cols-12 gap-4">

            {/* Spend bar chart */}
            <div className="col-span-12 lg:col-span-8 card p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="label mb-1">Cloud Spend</p>
                  {loading ? <Skeleton className="h-8 w-36" /> : (
                    <div className="flex items-end gap-3">
                      <span className="stat-number text-3xl">
                        ${((summary?.total_spend ?? 0) / 1000).toFixed(1)}k
                      </span>
                      {summary?.spend_change_pct !== 0 && (
                        <span className={`text-xs mb-1 ${(summary?.spend_change_pct ?? 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                          {(summary?.spend_change_pct ?? 0) >= 0 ? '↑' : '↓'} {Math.abs(summary?.spend_change_pct ?? 0)}%
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1 bg-bg rounded-xl p-1">
                  {PERIODS.map(p => (
                    <button
                      key={p}
                      onClick={() => setPeriod(p)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                        p === period ? 'bg-accent text-white' : 'text-secondary hover:text-primary'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              {loading ? (
                <Skeleton className="h-44" />
              ) : barData.length > 0 ? (
                <SpendBarChart data={barData} activeIndex={activeBarIdx} />
              ) : (
                <div className="h-44 flex items-center justify-center text-xs text-secondary">
                  Upload a CSV to see spend data
                </div>
              )}
            </div>

            {/* AI panel */}
            <div className="col-span-12 lg:col-span-4">
              <AiInsightPanel
                summary={
                  summary?.record_count
                    ? `${activeOrg?.name ?? 'Your org'} has spent $${((summary.total_spend ?? 0) / 1000).toFixed(1)}k across ${providers.length} provider(s). ${
                        summary.anomaly_count > 0
                          ? `${summary.anomaly_count} anomal${summary.anomaly_count === 1 ? 'y' : 'ies'} detected — check the Anomalies tab.`
                          : 'No anomalies detected this period.'
                      }`
                    : null
                }
                stats={[
                  {
                    label: 'Anomalies',
                    value: summary?.anomaly_count ?? 0,
                    badge: (summary?.anomaly_count ?? 0) > 0 ? 'Review' : 'Clear',
                    badgeVariant: (summary?.anomaly_count ?? 0) > 0 ? 'danger' : 'success',
                  },
                  {
                    label: 'Records',
                    value: summary?.record_count ?? 0,
                    badge: 'Loaded',
                    badgeVariant: 'accent',
                  },
                ]}
              />
            </div>
          </div>

          {/* Second row */}
          <div className="grid grid-cols-12 gap-4">

            {/* Donut */}
            <div className="col-span-12 lg:col-span-4 card p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-primary">Spend by Service</span>
                <span className="label">All time</span>
              </div>
              {loading ? <Skeleton className="h-40" /> : donutData.data.length > 0 ? (
                <SpendDonutChart data={donutData.data} total={donutData.total} />
              ) : (
                <div className="h-40 flex items-center justify-center text-xs text-secondary">No data yet</div>
              )}
            </div>

            {/* Provider breakdown */}
            <div className="col-span-12 lg:col-span-4">
              {loading ? <Skeleton className="h-full min-h-[180px]" /> : (
                <ProviderBreakdown providers={providers} />
              )}
            </div>

            {/* Top services table */}
            <div className="col-span-12 lg:col-span-4 card p-5 flex flex-col gap-4">
              <span className="text-sm font-semibold text-primary">Top Services by Cost</span>
              {loading ? <Skeleton className="h-40" /> : donutData.data.length > 0 ? (
                <div className="flex flex-col divide-y divide-border">
                  {donutData.data.map((s, i) => (
                    <div key={i} className="flex items-center justify-between py-2.5">
                      <div className="flex items-center gap-3">
                        <span className="text-[11px] font-mono text-secondary w-4">{i + 1}</span>
                        <span className="text-xs text-primary font-medium">{s.name}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-secondary">{s.pct}%</span>
                        <span className="text-xs font-semibold text-primary font-mono">
                          ${Number(s.value).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-40 flex items-center justify-center text-xs text-secondary">No data yet</div>
              )}
            </div>
          </div>

          {/* Third row */}
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-12 lg:col-span-6">
              <RecentAnomalies anomalies={anomalies} />
            </div>

            {/* Spend summary card */}
            <div className="col-span-12 lg:col-span-6 card p-5 flex flex-col gap-4">
              <span className="text-sm font-semibold text-primary">30-Day Spend Summary</span>
              {loading ? <Skeleton className="h-32" /> : (
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Last 30 Days',   value: `$${((summary?.spend_last_30d ?? 0) / 1000).toFixed(1)}k`,  color: 'text-primary' },
                    { label: 'Change vs Prev',  value: `${(summary?.spend_change_pct ?? 0) >= 0 ? '+' : ''}${summary?.spend_change_pct ?? 0}%`, color: (summary?.spend_change_pct ?? 0) >= 0 ? 'text-success' : 'text-danger' },
                    { label: 'Total Records',   value: (summary?.record_count ?? 0).toLocaleString(),             color: 'text-primary' },
                    { label: 'Anomaly Rate',    value: summary?.record_count ? `${((summary.anomaly_count / summary.record_count) * 100).toFixed(1)}%` : '—', color: 'text-warning' },
                  ].map((item, i) => (
                    <div key={i} className="bg-bg rounded-xl p-4 flex flex-col gap-1">
                      <span className="text-[11px] text-secondary">{item.label}</span>
                      <span className={`text-xl font-semibold ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
