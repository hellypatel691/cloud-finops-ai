import clsx from 'clsx'

export default function Input({ label, error, className, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs text-secondary font-medium">{label}</label>}
      <input
        className={clsx(
          'w-full bg-bg border border-border rounded-xl px-3 py-2 text-sm text-primary placeholder-muted outline-none',
          'focus:border-accent/60 transition-colors duration-150',
          error && 'border-danger/60',
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-danger">{error}</p>}
    </div>
  )
}
