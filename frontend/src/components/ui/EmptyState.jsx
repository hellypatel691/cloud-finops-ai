export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      {Icon && (
        <div className="w-12 h-12 rounded-2xl bg-border flex items-center justify-center text-secondary mb-1">
          <Icon size={22} />
        </div>
      )}
      <p className="text-sm font-medium text-primary">{title}</p>
      {description && <p className="text-xs text-secondary max-w-xs">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
