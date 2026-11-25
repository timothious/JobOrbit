import { Settings } from 'lucide-react'
import { EmptyState, PageHeader, Tabs, type TabItem } from '@/components'
import { useTabParam } from '@/hooks'

const tabs: TabItem[] = [
  { id: 'general', label: 'General' },
  { id: 'sources', label: 'Job Sources' },
  { id: 'sync-logs', label: 'Sync Logs' },
  { id: 'scoring', label: 'Scoring' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'data', label: 'Data & Backup' },
]

export function SettingsPage() {
  const activeId = useTabParam(tabs.map((tab) => tab.id))
  const active = tabs.find((tab) => tab.id === activeId)!

  return (
    <>
      <PageHeader title="Settings and Job Sources" description="Configure the app, sources, scoring and backups." />
      <Tabs tabs={tabs} activeId={activeId} label="Settings sections" />
      <EmptyState
        icon={Settings}
        title={active.label}
        description="Nothing to show here yet."
      />
    </>
  )
}
