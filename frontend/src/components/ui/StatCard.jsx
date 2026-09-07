import clsx from 'clsx'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatCard({ title, value, change, changeLabel, icon: Icon, accent = false }) {
  const isPositive = change >= 0

  return (
    <div className={clsx('card p-5 flex flex-col gap-3', accent && 'border-accent/30 shadow-glow')}>
      <div className="flex items-center justify-between">
        <span className="label">{title}</span>
        {Icon && (
          <div className="w-8 h-8 rounded-xl bg-border flex items-center justify-center text-secondary">
            <Icon size={14} />
          </div>
        )}
      </div>

      <div className="flex items-end gap-3">
        <span className="stat-number text-3xl">{value}</span>
        {change !== undefined && (
          <div className={clsx(
            'flex items-center gap-1 text-xs font-medium px-1.5 py-0.5 rounded-md mb-0.5',
            isPositive ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
          )}>
            {isPositive ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
            {Math.abs(change)}%
          </div>
        )}
      </div>

      {changeLabel && (
        <p className="text-xs text-secondary">{changeLabel}</p>
      )}
    </div>
  )
}
