import {
  BarChart3,
  Bell,
  Bookmark,
  BriefcaseBusiness,
  Globe2,
  KanbanSquare,
  LayoutDashboard,
  Settings,
  UserRound,
  type LucideIcon,
} from 'lucide-react'

export interface NavItem {
  label: string
  to: string
  icon: LucideIcon
}

export const primaryNav: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Jobs', to: '/jobs', icon: BriefcaseBusiness },
  { label: 'Tracker', to: '/applications', icon: KanbanSquare },
  { label: 'Countries', to: '/countries', icon: Globe2 },
]

export const secondaryNav: NavItem[] = [
  { label: 'Saved', to: '/saved', icon: Bookmark },
  { label: 'Opportunities', to: '/opportunities', icon: BarChart3 },
  { label: 'Profile', to: '/profile', icon: UserRound },
  { label: 'Notifications', to: '/notifications', icon: Bell },
  { label: 'Settings', to: '/settings', icon: Settings },
]

export function findNavItem(pathname: string): NavItem | undefined {
  return [...primaryNav, ...secondaryNav].find(({ to }) =>
    to === '/' ? pathname === '/' : pathname === to || pathname.startsWith(`${to}/`),
  )
}
