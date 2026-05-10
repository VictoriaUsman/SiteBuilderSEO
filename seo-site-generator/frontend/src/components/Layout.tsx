import { NavLink } from 'react-router-dom'
import { LayoutDashboard, History, Settings, Zap } from 'lucide-react'

const nav = [
  { to: '/', label: 'Generate', icon: LayoutDashboard },
  { to: '/jobs', label: 'Jobs', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-200">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 border-r border-slate-800 flex flex-col">
        <div className="p-5 border-b border-slate-800 flex items-center gap-2">
          <Zap size={20} className="text-sky-400" />
          <span className="font-bold text-white text-sm">SEO Builder</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800 text-xs space-y-0.5">
          <p className="text-slate-500">AI Local SEO Builder v1.0</p>
          <p className="text-slate-600">Built by <span className="text-slate-400 font-medium">Ian Tristan Cultura</span></p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}
