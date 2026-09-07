import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  FolderOpen,
  Upload,
  Receipt,
  AlertTriangle,
  TrendingUp,
  Settings,
  LogOut,
  Zap,
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/dashboard',      icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/organizations',  icon: Building2,        label: 'Organizations' },
  { to: '/anomalies',      icon: AlertTriangle,    label: 'Anomalies' },
  { to: '/forecast',       icon: TrendingUp,       label: 'Forecast' },
]

const bottomItems = [
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="flex flex-col items-center w-16 h-full bg-surface border-r border-border py-4 gap-2 shrink-0">
      {/* Logo */}
      <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent mb-4">
        <Zap size={18} className="text-white" />
      </div>

      {/* Nav */}
      <nav className="flex flex-col items-center gap-1 flex-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            title={label}
            className={({ isActive }) =>
              clsx(
                'flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-150',
                isActive
                  ? 'bg-accent text-white shadow-glow'
                  : 'text-secondary hover:bg-border hover:text-primary'
              )
            }
          >
            <Icon size={18} />
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="flex flex-col items-center gap-1">
        {bottomItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            title={label}
            className="flex items-center justify-center w-10 h-10 rounded-xl text-secondary hover:bg-border hover:text-primary transition-all duration-150"
          >
            <Icon size={18} />
          </NavLink>
        ))}
        <button
          title="Logout"
          className="flex items-center justify-center w-10 h-10 rounded-xl text-secondary hover:bg-border hover:text-danger transition-all duration-150"
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  )
}
