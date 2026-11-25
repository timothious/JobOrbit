import { Link } from 'react-router'

export interface TabItem {
  id: string
  label: string
}

interface TabsProps {
  tabs: readonly TabItem[]
  activeId: string
  label: string
}

export function Tabs({ tabs, activeId, label }: TabsProps) {
  return (
    <nav aria-label={label} className="mb-4 flex gap-1 overflow-x-auto border-b border-slate-200">
      {tabs.map((tab) => {
        const active = tab.id === activeId
        return (
          <Link
            key={tab.id}
            to={{ search: `?tab=${tab.id}` }}
            replace
            aria-current={active ? 'page' : undefined}
            className={`-mb-px whitespace-nowrap border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              active
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </Link>
        )
      })}
    </nav>
  )
}
