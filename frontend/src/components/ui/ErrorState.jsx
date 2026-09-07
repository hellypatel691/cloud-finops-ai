import { AlertTriangle, RefreshCw } from 'lucide-react'
import Button from './Button'

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <div className="w-12 h-12 rounded-2xl bg-danger/10 flex items-center justify-center text-danger mb-1">
        <AlertTriangle size={22} />
      </div>
      <p className="text-sm font-medium text-primary">Failed to load data</p>
      <p className="text-xs text-secondary max-w-sm">
        {error?.includes('Network') || error?.includes('fetch') || error?.includes('ECONNREFUSED')
          ? 'Cannot reach the backend. Make sure the API server is running on port 8000.'
          : error}
      </p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="mt-1">
          <RefreshCw size={12} /> Retry
        </Button>
      )}
    </div>
  )
}
