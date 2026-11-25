import { BarChart3 } from 'lucide-react'
import { EmptyState, PageHeader, Tabs, type TabItem } from '@/components'
import { useTabParam } from '@/hooks'

const tabs: TabItem[] = [
  { id: 'rankings', label: 'Rankings' },
  { id: 'matches', label: 'Job Matches' },
  { id: 'pathways', label: 'Pathways' },
  { id: 'evidence', label: 'Evidence Library' },
  { id: 'employers', label: 'Employer Signals' },
]

export function OpportunitiesPage() {
  const activeId = useTabParam(tabs.map((tab) => tab.id))
  const active = tabs.find((tab) => tab.id === activeId)!

  return (
    <>
      <PageHeader title="Opportunity Intelligence" description="Rankings, matches, pathways and evidence by country." />
      <Tabs tabs={tabs} activeId={activeId} label="Opportunities sections" />
      <EmptyState
        icon={BarChart3}
        title={active.label}
        description="Nothing to show here yet."
      />
    </>
  )
}
