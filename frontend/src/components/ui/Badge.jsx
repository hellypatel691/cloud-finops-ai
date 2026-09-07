import clsx from 'clsx'

const variants = {
  success: 'bg-success/10 text-success',
  danger:  'bg-danger/10 text-danger',
  warning: 'bg-warning/10 text-warning',
  info:    'bg-info/10 text-info',
  accent:  'bg-accent/10 text-accent-light',
  muted:   'bg-border text-secondary',
}

export default function Badge({ children, variant = 'muted', className }) {
  return (
    <span className={clsx(
      'inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-md',
      variants[variant],
      className
    )}>
      {children}
    </span>
  )
}
