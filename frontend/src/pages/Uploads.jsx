import { useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Upload, CheckCircle, XCircle, Clock, Loader, ArrowLeft, FileText } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getUploads, uploadCSV } from '../api/uploads'
import { getOrganization } from '../api/organizations'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import ErrorState from '../components/ui/ErrorState'

const statusConfig = {
  completed:  { icon: CheckCircle, variant: 'success', label: 'Completed' },
  failed:     { icon: XCircle,     variant: 'danger',  label: 'Failed' },
  processing: { icon: Loader,      variant: 'info',    label: 'Processing' },
  pending:    { icon: Clock,       variant: 'warning', label: 'Pending' },
}

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

export default function Uploads() {
  const { orgId } = useParams()
  const { data: org }     = useApi(() => getOrganization(orgId), [orgId])
  const { data: uploads, loading, error, refetch } = useApi(() => getUploads(orgId), [orgId])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver]   = useState(false)
  const fileRef = useRef()

  const handleFile = async (file) => {
    if (!file) return
    setUploading(true)
    try { await uploadCSV(orgId, file); refetch() }
    catch (e) { alert(e.message) }
    finally { setUploading(false) }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/organizations" className="w-8 h-8 rounded-xl bg-card border border-border flex items-center justify-center text-secondary hover:text-primary transition-colors">
            <ArrowLeft size={14} />
          </Link>
          <div>
            <h2 className="text-base font-semibold text-primary">{org?.name ?? 'Organization'} — Uploads</h2>
            <p className="text-xs text-secondary mt-0.5">Upload cloud billing CSV files</p>
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => fileRef.current?.click()}
        className={`card p-8 flex flex-col items-center gap-3 cursor-pointer transition-all ${
          dragOver ? 'border-accent bg-accent/5' : 'hover:border-accent/40'
        }`}
      >
        <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={e => handleFile(e.target.files[0])} />
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-colors ${dragOver ? 'bg-accent text-white' : 'bg-border text-secondary'}`}>
          {uploading ? <Loader size={20} className="animate-spin" /> : <Upload size={20} />}
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-primary">
            {uploading ? 'Uploading…' : 'Drop your CSV here or click to browse'}
          </p>
          <p className="text-xs text-secondary mt-1">AWS, Azure, GCP billing exports supported · Max 50 MB</p>
        </div>
      </div>

      {/* Upload history */}
      <div className="card flex flex-col">
        <div className="px-5 py-4 border-b border-border">
          <span className="text-sm font-semibold text-primary">Upload History</span>
        </div>

        {loading ? (
          <div className="p-5 flex flex-col gap-3">
            {Array.from({ length: 3 }).map((_, i) => <div key={i} className="h-12 bg-border animate-pulse rounded-xl" />)}
          </div>
        ) : error ? (
          <ErrorState error={error} onRetry={refetch} />
        ) : uploads?.length === 0 ? (
          <EmptyState icon={FileText} title="No uploads yet" description="Upload a CSV to start ingesting billing data." />
        ) : (
          <div className="divide-y divide-border">
            {uploads.map(u => {
              const s = statusConfig[u.status] ?? statusConfig.pending
              const StatusIcon = s.icon
              return (
                <div key={u.id} className="flex items-center justify-between px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-border flex items-center justify-center text-secondary">
                      <FileText size={14} />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-primary">{u.filename}</p>
                      <p className="text-[11px] text-secondary">{formatDate(u.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {u.row_count != null && (
                      <span className="text-xs text-secondary">{u.row_count.toLocaleString()} rows</span>
                    )}
                    <Badge variant={s.variant}>
                      <StatusIcon size={10} className={u.status === 'processing' ? 'animate-spin' : ''} />
                      {s.label}
                    </Badge>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
