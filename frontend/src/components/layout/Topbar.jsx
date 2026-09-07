import { Search, Bell, LogOut } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const pageTitles = {
  '/dashboard':    'Overview',
  '/organizations':'Organizations',
  '/anomalies':    'Anomalies',
  '/forecast':     'Forecast',
  '/settings':     'Settings',
}

export default function Topbar() {
  const { pathname }    = useLocation()
  const { user, logout } = useAuth()
  const navigate        = useNavigate()
  const title           = pageTitles[pathname] ?? 'Cloud FinOps AI'

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.[0]?.toUpperCase() ?? 'U'

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="flex items-center justify-between px-6 h-14 border-b border-border bg-surface shrink-0">
      <h1 className="text-base font-semibold text-primary">{title}</h1>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="flex items-center gap-2 bg-card border border-border rounded-xl px-3 h-8 w-52">
          <Search size={13} className="text-secondary shrink-0" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent text-xs text-primary placeholder-secondary outline-none w-full"
          />
        </div>

        {/* Bell */}
        <button className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-card border border-border text-secondary hover:text-primary transition-colors">
          <Bell size={14} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-accent" />
        </button>

        {/* User pill */}
        <div className="flex items-center gap-2 bg-card border border-border rounded-xl px-2.5 h-8">
          <div className="w-5 h-5 rounded-full bg-accent flex items-center justify-center text-white text-[10px] font-semibold">
            {initials}
          </div>
          <span className="text-xs text-primary font-medium max-w-[100px] truncate">
            {user?.full_name ?? user?.email ?? 'User'}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          title="Sign out"
          className="flex items-center justify-center w-8 h-8 rounded-xl bg-card border border-border text-secondary hover:text-danger hover:border-danger/40 transition-colors"
        >
          <LogOut size={13} />
        </button>
      </div>
    </header>
  )
}
