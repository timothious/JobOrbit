import { Circle } from 'lucide-react'
import { Link } from 'react-router'
import { Card } from '@/components'

const steps = [
  { label: 'Complete your profile', to: '/profile' },
  { label: 'Enable job sources', to: '/settings?tab=sources' },
  { label: 'Run your first sync', to: '/settings?tab=sync-logs' },
  { label: 'Add immigration pathways', to: '/opportunities?tab=pathways' },
]

export function FirstRunChecklist() {
  return (
    <Card>
      <h2 className="text-base font-semibold">Get started</h2>
      <ul className="mt-3 space-y-1">
        {steps.map(({ label, to }) => (
          <li key={to}>
            <Link
              to={to}
              className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
            >
              <Circle size={16} strokeWidth={1.75} className="text-slate-400" aria-hidden="true" />
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </Card>
  )
}
