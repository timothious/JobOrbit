import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { useState } from 'react'
import { NavLink } from 'react-router'
import { primaryNav, secondaryNav } from '@/config/navigation'

const STORAGE_KEY = 'joborbit.sidebarCollapsed'

function readCollapsed() {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(readCollapsed)

  const toggle = () => {
    setCollapsed(!collapsed)
    try {
      localStorage.setItem(STORAGE_KEY, String(!collapsed))
    } catch {
      // Storage unavailable (private mode); the state still applies for this session.
    }
  }
  const Toggle = collapsed ? PanelLeftOpen : PanelLeftClose

  return (
    <aside
      className={`hidden shrink-0 flex-col border-r border-slate-200 bg-white md:flex ${
        collapsed ? 'w-14' : 'w-55'
      }`}
    >
      <div className="flex h-12 items-center px-4 text-base font-semibold text-blue-700">
        {collapsed ? 'JO' : 'JobOrbit'}
      </div>
      <nav aria-label="Main" className="flex flex-1 flex-col gap-1 p-2">
        {[...primaryNav, ...secondaryNav].map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium ${
                isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            <Icon size={18} strokeWidth={1.75} aria-hidden="true" />
            {!collapsed && label}
            {collapsed && <span className="sr-only">{label}</span>}
          </NavLink>
        ))}
      </nav>
      <button
        type="button"
        onClick={toggle}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        className="m-2 flex items-center gap-3 rounded-md px-2.5 py-2 text-sm text-slate-600 hover:bg-slate-100"
      >
        <Toggle size={18} strokeWidth={1.75} aria-hidden="true" />
        {!collapsed && 'Collapse'}
      </button>
    </aside>
  )
}
