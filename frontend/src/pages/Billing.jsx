import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Receipt, ArrowLeft, Search } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getBilling } from '../api/billing'
import { getOrganization } from '../api/organizations'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import ErrorState from '../components/ui/ErrorState'

const PROVIDERS = { AWS: 'warning', Azure: 'info', GCP: 'success' }

export default function Billing() {
  const { orgId } = useParams()
  const { data: org }     = useApi(() => getOrganization(orgId), [orgId])
  const { data: records, loading, error, refetch } = useApi(() => getBilling(orgId), [orgId])
  const [search, setSearch] = useState('')

  const filtered = (records ?? []).filter(r =>
    !search ||
    r.service.toLowerCase().includes(search.toLowerCase()) ||
    r.cloud_provider.toLowerCase().includes(search.toLowerCase()) ||
    r.environment?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/organizations" className="w-8 h-8 rounded-xl bg-card border border-border flex items-center justify-center text-secondary hover:text-primary transition-colors">
            <ArrowLeft size={14} />
          </Link>
          <div>
            <h2 className="text-base font-semibold text-primary">{org?.name ?? 'Organization'} — Billing</h2>
            <p className="text-xs text-secondary mt-0.5">{records?.length?.toLocaleString() ?? 0} billing records</p>
          </div>
        </div>

        {/* Search */}
        <div className="flex items-center gap-2 bg-card border border-border rounded-xl px-3 h-9 w-56">
          <Search size={13} className="text-secondary" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Filter by service, provider..."
            className="bg-transparent text-xs text-primary placeholder-muted outline-none w-full"
          />
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {['Date', 'Provider', 'Service', 'Environment', 'Region', 'Cost', 'Anomaly'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-[11px] font-medium text-secondary whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-3 bg-border animate-pulse rounded" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <EmptyState icon={Receipt} title="No billing records" description="Upload a CSV to see billing data here." />
                  </td>
                </tr>
              ) : (
                filtered.slice(0, 200).map((r, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-border/20 transition-colors">
                    <td className="px-4 py-2.5 text-secondary font-mono">{r.date}</td>
                    <td className="px-4 py-2.5">
                      <Badge variant={PROVIDERS[r.cloud_provider] ?? 'muted'}>{r.cloud_provider}</Badge>
                    </td>
                    <td className="px-4 py-2.5 text-primary font-medium">{r.service}</td>
                    <td className="px-4 py-2.5 text-secondary">{r.environment ?? '—'}</td>
                    <td className="px-4 py-2.5 text-secondary">{r.region ?? '—'}</td>
                    <td className="px-4 py-2.5 text-primary font-semibold font-mono">
                      ${Number(r.total_cost).toFixed(2)}
                    </td>
                    <td className="px-4 py-2.5">
                      {r.is_anomaly
                        ? <Badge variant="danger">⚠ Yes</Badge>
                        : <span className="text-muted">—</span>
                      }
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 200 && (
          <div className="px-5 py-3 border-t border-border text-xs text-secondary">
            Showing 200 of {filtered.length.toLocaleString()} records
          </div>
        )}
      </div>
    </div>
  )
}
