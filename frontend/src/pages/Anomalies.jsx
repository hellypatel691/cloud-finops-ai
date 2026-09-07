import { useState } from 'react'
import { AlertTriangle, Zap, TrendingUp, BarChart2 } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getOrganizations } from '../api/organizations'
import { getAnomalies } from '../api/anomalies'
import { getExplainability } from '../api/explainability'
import Badge from '../components/ui/Badge'
import ErrorState from '../components/ui/ErrorState'
import EmptyState from '../components/ui/EmptyState'
import ShapPanel from '../components/dashboard/ShapPanel'
import RootCausePanel from '../components/dashboard/RootCausePanel'

const providerVariant = { AWS: 'warning', Azure: 'info', GCP: 'success' }
const typeVariant     = { Spike: 'danger', Drift: 'warning', Seasonal: 'info', Normal: 'muted' }

function ScoreBar({ score, color = 'bg-danger' }) {
  return (
    <div className="flex items-center gap-2 w-28">
      <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-[11px] text-secondary font-mono">{score.toFixed(2)}</span>
    </div>
  )
}

function scoreColor(s) {
  if (s >= 0.8) return 'bg-danger'
  if (s >= 0.6) return 'bg-warning'
  return 'bg-info'
}

export default function Anomalies() {
  const [activeOrgIdx, setActiveOrgIdx] = useState(0)
  const { data: orgs, loading: orgsLoading, error: orgsError } = useApi(getOrganizations)
  const activeOrg = orgs?.[activeOrgIdx]

  const {
    data: result,
    loading: mlLoading,
    error: mlError,
    refetch,
  } = useApi(
    () => activeOrg ? getAnomalies(activeOrg.id) : Promise.resolve(null),
    [activeOrg?.id]
  )

  const {
    data: explainData,
    loading: explainLoading,
  } = useApi(
    () => activeOrg ? getExplainability(activeOrg.id) : Promise.resolve(null),
    [activeOrg?.id]
  )

  const loading  = orgsLoading || mlLoading
  const error    = orgsError || mlError
  const anomalies = result?.anomalies ?? []

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-primary">Anomalies</h2>
        <p className="text-xs text-secondary mt-0.5">
          Ensemble: Z-score · IQR · Seasonal decomposition · Isolation Forest · One-Class SVM
        </p>
      </div>

      {/* Org selector */}
      {orgs && orgs.length > 0 && (
        <div className="flex items-center gap-2">
          {orgs.map((org, i) => (
            <button
              key={org.id}
              onClick={() => setActiveOrgIdx(i)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                i === activeOrgIdx ? 'bg-accent text-white' : 'bg-card border border-border text-secondary hover:text-primary'
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
          {/* Summary stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                label: 'Total Anomalies',
                value: loading ? '…' : result?.total_anomalies ?? 0,
                sub:   loading ? '' : `${((result?.anomaly_rate ?? 0) * 100).toFixed(1)}% of records`,
                color: 'text-danger',
                icon:  AlertTriangle,
              },
              {
                label: 'Highest Cost',
                value: loading ? '…' : result?.highest_cost ? `$${Number(result.highest_cost).toFixed(2)}` : '—',
                sub:   'single anomalous record',
                color: 'text-warning',
                icon:  Zap,
              },
              {
                label: 'Avg Score',
                value: loading ? '…' : result?.avg_score?.toFixed(3) ?? '—',
                sub:   'ensemble anomaly score',
                color: 'text-accent-light',
                icon:  BarChart2,
              },
              {
                label: 'Providers',
                value: loading ? '…' : result?.providers?.length ?? '—',
                sub:   loading ? '' : (result?.providers ?? []).join(' · ') || 'no data',
                color: 'text-info',
                icon:  TrendingUp,
              },
            ].map((s, i) => (
              <div key={i} className="card p-5 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="label">{s.label}</span>
                  <s.icon size={14} className={s.color} />
                </div>
                <span className={`text-2xl font-semibold ${s.color}`}>{s.value}</span>
                <span className="text-xs text-secondary">{s.sub}</span>
              </div>
            ))}
          </div>

          {/* Top services */}
          {!loading && result?.top_services?.length > 0 && (
            <div className="card p-5 flex flex-col gap-3">
              <span className="text-sm font-semibold text-primary">Top Services by Anomaly Count</span>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {result.top_services.map((s, i) => (
                  <div key={i} className="bg-bg rounded-xl p-3 flex flex-col gap-1">
                    <span className="text-xs font-medium text-primary truncate">{s.service}</span>
                    <span className="text-lg font-semibold text-danger">{s.count}</span>
                    <span className="text-[10px] text-secondary">anomalies</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Anomaly table */}
          <div className="card overflow-hidden">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <span className="text-sm font-semibold text-primary">
                Detected Anomalies
                {!loading && anomalies.length > 0 && (
                  <span className="ml-2 text-xs text-secondary font-normal">
                    ({anomalies.length} of {result?.total_records?.toLocaleString()} records)
                  </span>
                )}
              </span>
              <Badge variant="accent">ML Ensemble Active</Badge>
            </div>

            {loading ? (
              <div className="divide-y divide-border">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-4 px-5 py-4">
                    <div className="w-9 h-9 bg-border rounded-xl animate-pulse" />
                    <div className="flex-1 flex flex-col gap-2">
                      <div className="h-3 w-40 bg-border animate-pulse rounded" />
                      <div className="h-2 w-28 bg-border animate-pulse rounded" />
                    </div>
                    <div className="w-24 h-3 bg-border animate-pulse rounded" />
                  </div>
                ))}
                <p className="px-5 py-3 text-xs text-secondary italic">
                  Running ML models — this may take a few seconds…
                </p>
              </div>
            ) : anomalies.length === 0 ? (
              <EmptyState
                icon={AlertTriangle}
                title={result ? 'No anomalies detected' : 'No data loaded'}
                description={
                  !activeOrg
                    ? 'Create an organization and upload billing data first.'
                    : result
                    ? 'All billing records are within normal ranges.'
                    : 'Upload a CSV file to run anomaly detection.'
                }
              />
            ) : (
              <div className="divide-y divide-border">
                {anomalies.slice(0, 150).map((a, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between px-5 py-3 hover:bg-border/10 transition-colors"
                  >
                    {/* Left */}
                    <div className="flex items-center gap-4">
                      <div className="w-9 h-9 rounded-xl bg-danger/10 flex items-center justify-center shrink-0">
                        <AlertTriangle size={14} className="text-danger" />
                      </div>
                      <div>
                        <p className="text-xs font-medium text-primary">{a.service}</p>
                        <p className="text-[11px] text-secondary">
                          {a.date} · {a.environment} · {a.region}
                        </p>
                      </div>
                    </div>

                    {/* Right */}
                    <div className="flex items-center gap-3 shrink-0">
                      <Badge variant={providerVariant[a.cloud_provider] ?? 'muted'}>
                        {a.cloud_provider}
                      </Badge>
                      <Badge variant={typeVariant[a.anomaly_type] ?? 'muted'}>
                        {a.anomaly_type}
                      </Badge>
                      <ScoreBar score={a.anomaly_score} color={scoreColor(a.anomaly_score)} />
                      <span className="text-sm font-semibold text-danger font-mono w-20 text-right">
                        ${a.total_cost.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {anomalies.length > 150 && (
              <div className="px-5 py-3 border-t border-border text-xs text-secondary">
                Showing 150 of {anomalies.length} anomalies
              </div>
            )}
          </div>

          {/* SHAP + Root Cause */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ShapPanel
              globalImportance={explainData?.shap?.global_importance ?? []}
              recordExplanations={explainData?.shap?.record_explanations ?? []}
              loading={explainLoading}
            />
            <RootCausePanel
              rootCause={explainData?.root_cause}
              loading={explainLoading}
            />
          </div>
        </>
      )}
    </div>
  )
}
