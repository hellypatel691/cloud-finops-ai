import { AlertTriangle, ArrowUpRight } from 'lucide-react'
import Badge from '../ui/Badge'
import { Link } from 'react-router-dom'

export default function RecentAnomalies({ anomalies = [] }) {
  return (
    <div className="card p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-primary">Recent Anomalies</span>
        <Link to="/anomalies" className="flex items-center gap-1 text-xs text-accent hover:text-accent-light transition-colors">
          View all <ArrowUpRight size={11} />
        </Link>
      </div>

      {anomalies.length === 0 ? (
        <div className="flex flex-col items-center py-6 gap-2">
          <div className="w-9 h-9 rounded-xl bg-border flex items-center justify-center text-secondary">
            <AlertTriangle size={16} />
          </div>
          <p className="text-xs text-secondary">No anomalies detected</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {anomalies.map((a, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
              <div className="flex flex-col gap-0.5">
                <span className="text-xs text-primary font-medium">{a.service}</span>
                <span className="text-[11px] text-secondary">{a.date} · {a.provider}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-danger">${Number(a.cost).toLocaleString()}</span>
                <Badge variant="danger">Anomaly</Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
