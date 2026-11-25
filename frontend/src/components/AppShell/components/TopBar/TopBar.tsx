import { Bell } from 'lucide-react'
import { Link, useLocation } from 'react-router'
import { findNavItem } from '@/config/navigation'

export function TopBar() {
  const { pathname } = useLocation()

  return (
    <header className="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4">
      <span className="font-semibold text-slate-900 md:hidden">
        {findNavItem(pathname)?.label ?? 'JobOrbit'}
      </span>
      <Link
        to="/notifications"
        aria-label="Notifications"
        className="ml-auto rounded-md p-2 text-slate-600 hover:bg-slate-100"
      >
        <Bell size={18} strokeWidth={1.75} aria-hidden="true" />
      </Link>
    </header>
  )
}
