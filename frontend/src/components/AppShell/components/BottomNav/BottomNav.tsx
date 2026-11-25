import { Ellipsis } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink, useLocation } from 'react-router'
import { findNavItem, primaryNav, secondaryNav } from '@/config/navigation'

const itemClass = 'flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-medium'

export function BottomNav() {
  const { pathname } = useLocation()
  const [moreOpen, setMoreOpen] = useState(false)
  const navRef = useRef<HTMLElement>(null)
  const current = findNavItem(pathname)
  const moreActive = current !== undefined && secondaryNav.includes(current)

  useEffect(() => {
    if (!moreOpen) return

    const close = (event: Event) => {
      if (event instanceof KeyboardEvent ? event.key === 'Escape' : !navRef.current?.contains(event.target as Node)) {
        setMoreOpen(false)
      }
    }
    document.addEventListener('pointerdown', close)
    document.addEventListener('keydown', close)
    return () => {
      document.removeEventListener('pointerdown', close)
      document.removeEventListener('keydown', close)
    }
  }, [moreOpen])

  return (
    <nav
      ref={navRef}
      aria-label="Main"
      className="relative flex shrink-0 border-t border-slate-200 bg-white pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      {primaryNav.map(({ label, to, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) => `${itemClass} ${isActive ? 'text-blue-700' : 'text-slate-600'}`}
        >
          <Icon size={18} strokeWidth={1.75} aria-hidden="true" />
          {label}
        </NavLink>
      ))}
      <button
        type="button"
        aria-expanded={moreOpen}
        aria-controls="more-menu"
        onClick={() => setMoreOpen(!moreOpen)}
        className={`${itemClass} ${moreActive ? 'text-blue-700' : 'text-slate-600'}`}
      >
        <Ellipsis size={18} strokeWidth={1.75} aria-hidden="true" />
        More
      </button>
      {moreOpen && (
        <ul
          id="more-menu"
          className="absolute right-2 bottom-full mb-2 w-48 rounded-lg border border-slate-200 bg-white p-1 shadow-lg"
        >
          {secondaryNav.map(({ label, to, icon: Icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                onClick={() => setMoreOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2 text-sm ${
                    isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-700 hover:bg-slate-100'
                  }`
                }
              >
                <Icon size={18} strokeWidth={1.75} aria-hidden="true" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      )}
    </nav>
  )
}
