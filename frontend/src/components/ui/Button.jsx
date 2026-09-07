import clsx from 'clsx'

const variants = {
  primary:  'bg-accent hover:bg-accent-light text-white',
  ghost:    'bg-transparent hover:bg-border text-secondary hover:text-primary',
  outline:  'bg-transparent border border-border hover:border-accent text-secondary hover:text-primary',
  danger:   'bg-danger/10 hover:bg-danger/20 text-danger',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs rounded-lg',
  md: 'px-4 py-2 text-sm rounded-xl',
  lg: 'px-5 py-2.5 text-sm rounded-xl',
}

export default function Button({ children, variant = 'primary', size = 'md', className, ...props }) {
  return (
    <button
      className={clsx(
        'inline-flex items-center gap-2 font-medium transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
