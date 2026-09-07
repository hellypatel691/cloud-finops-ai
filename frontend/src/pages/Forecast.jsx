import { useState } from 'react'
import { TrendingUp, DollarSign, BarChart2, Cpu } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getOrganizations } from '../api/organizations'
import { getForecast } from '../api/forecast'
import Badge from '../components/ui/Badge'
import ErrorState from '../components/ui/ErrorState'
import ForecastLineChart from '../components/charts/ForecastLineChart'

const PROVIDER_COLORS = { AWS: '#f59e0b', Azure: '#38bdf8', GCP: '#4ade80' }

function Skeleton({ className = '' }) {
  return <div className={`bg-border animate-pulse rounded-xl ${className}`} />
}

export default function Forecast() {
  const [activeOrgIdx, setActiveOrgIdx] = useState(0)

  const { data: orgs, loading: orgsLoading, error: orgsError } = useApi(getOrganizations)
  const activeOrg = orgs?.[activeOrgIdx]

  const {
    data: result,
    loading: forecastLoading,
    error: forecastError,
    refetch,
  } = useApi(
    () => activeOrg ? getForecast(activeOrg.id) : Promise.resolve(null),
    [activeOrg?.id]
  )

  const loading = orgsLoading || forecastLoading
  const error   = orgsError || forecastError

  // Build chart-ready series — last 90 days actual + all forecast
  const chartData = (() => {
    if (!result?.series) return []
    const actual   = result.series.filter(p => !p.is_forecast).slice(-90)
    const forecast = result.series.filter(p => p.is_forecast)
    return [
      ...actual.map(p => ({ label: p.ds.slice(5), actual: p.actual ?? p.yhat })),
      ...forecast.map(p => ({ label: p.ds.slice(5), forecast: p.yhat })),
    ]
  })()

  const forecastStart = result?.series?.find(p => p.is_forecast)?.ds?.slice(5) ?? null

  const horizonVariants = ['success', 'warning', 'danger']

  const maxP90 = Math.max(...(result?.provider_breakdown ?? []).map(p => p.p90_30d), 1)

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h2 className="text-base font-semibold text-primary">Spend Forecast</h2>
        <p className="text-xs text-secondary mt-0.5">
          Prophet + LightGBM ensemble · Best model auto-selected by MAE
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
          {/* Horizon cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-28" />)
            ) : (
              (result?.horizons ?? []).map((h, i) => (
                <div key={i} className="card p-5 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="label">{h.days}-Day Forecast</span>
                    <Badge variant={horizonVariants[i]}>
                      {result?.selected_model ?? '—'}
                    </Badge>
                  </div>
                  <span className="stat-number text-2xl">
                    ${h.p50.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                  <div className="flex items-center gap-2 text-xs text-secondary">
                    <span className="text-success">P10 ${h.p10.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                    <span className="text-muted">·</span>
                    <span className="text-danger">P90 ${h.p90.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Main forecast chart */}
          <div className="card p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-semibold text-primary">Historical + Forecast (90 days)</span>
                {result?.forecast_start && (
                  <span className="ml-2 text-xs text-secondary">forecast from {result.forecast_start}</span>
                )}
              </div>
              <div className="flex items-center gap-4 text-xs text-secondary">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-accent inline-block rounded" /> Actual
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-success inline-block rounded" /> Forecast
                </span>
              </div>
            </div>
            {loading ? (
              <Skeleton className="h-48" />
            ) : chartData.length > 1 ? (
              <ForecastLineChart data={chartData} forecastStart={forecastStart} />
            ) : (
              <div className="h-48 flex items-center justify-center text-xs text-secondary">
                Upload billing data to generate a forecast
              </div>
            )}
          </div>

          {/* Provider breakdown */}
          <div className="card p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-primary">30-Day Forecast by Provider</span>
              <span className="text-xs text-secondary">P10 / P50 / P90 confidence bands</span>
            </div>
            {loading ? (
              <div className="flex flex-col gap-4">
                {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
              </div>
            ) : !result?.provider_breakdown?.length ? (
              <p className="text-xs text-secondary py-4 text-center">No billing data loaded</p>
            ) : (
              <div className="flex flex-col gap-5">
                {result.provider_breakdown.map((p, i) => {
                  const color = PROVIDER_COLORS[p.provider] ?? '#7B6EF6'
                  return (
                    <div key={i} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-primary">{p.provider}</span>
                        <span className="text-xs text-secondary font-mono">
                          ${p.p10_30d.toLocaleString(undefined, { maximumFractionDigits: 0 })} –
                          ${p.p90_30d.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                      </div>
                      <div className="relative h-3 bg-border rounded-full overflow-hidden">
                        <div
                          className="absolute h-full rounded-full opacity-25"
                          style={{
                            left:  `${(p.p10_30d / maxP90) * 100}%`,
                            width: `${((p.p90_30d - p.p10_30d) / maxP90) * 100}%`,
                            background: color,
                          }}
                        />
                        <div
                          className="absolute top-0.5 bottom-0.5 w-1.5 rounded-full"
                          style={{ left: `${(p.p50_30d / maxP90) * 100}%`, background: color }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-muted">
                        <span>P10 ${p.p10_30d.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        <span>P50 ${p.p50_30d.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                        <span>P90 ${p.p90_30d.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Model comparison */}
          <div className="card p-5 flex flex-col gap-4">
            <span className="text-sm font-semibold text-primary">Model Comparison</span>
            {loading ? (
              <Skeleton className="h-24" />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {(result?.models ?? []).map((m, i) => (
                  <div
                    key={i}
                    className={`bg-bg rounded-xl p-4 flex flex-col gap-2 border transition-colors ${
                      m.selected ? 'border-accent/40' : 'border-border'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-primary">{m.name}</span>
                      {m.selected
                        ? <Badge variant="accent">Selected</Badge>
                        : <Badge variant="muted">Not used</Badge>
                      }
                    </div>
                    {m.mae != null ? (
                      <div className="flex gap-4 text-xs">
                        <div>
                          <span className="text-secondary">MAE </span>
                          <span className="text-primary font-mono">${m.mae.toFixed(1)}</span>
                        </div>
                        {m.mape != null && (
                          <div>
                            <span className="text-secondary">MAPE </span>
                            <span className="text-primary font-mono">{m.mape.toFixed(1)}%</span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-muted">Not enough data</span>
                    )}
                  </div>
                ))}

                {/* Linear fallback card */}
                <div className={`bg-bg rounded-xl p-4 flex flex-col gap-2 border ${
                  result?.selected_model === 'Linear' ? 'border-accent/40' : 'border-border'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-primary">Linear Trend</span>
                    {result?.selected_model === 'Linear'
                      ? <Badge variant="accent">Fallback active</Badge>
                      : <Badge variant="muted">Fallback</Badge>
                    }
                  </div>
                  <span className="text-xs text-muted">
                    Used when Prophet + LightGBM unavailable
                  </span>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
