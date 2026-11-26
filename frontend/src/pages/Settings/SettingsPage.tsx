import { Settings } from 'lucide-react'
import { useSettings } from '@/api'
import { EmptyState, PageHeader, Skeleton, Tabs, type TabItem } from '@/components'
import { useTabParam } from '@/hooks'
import { ChangePasswordForm } from './components/ChangePasswordForm'
import { GeneralSettingsForm } from './components/GeneralSettingsForm'

const tabs: TabItem[] = [
  { id: 'general', label: 'General' },
  { id: 'sources', label: 'Job Sources' },
  { id: 'sync-logs', label: 'Sync Logs' },
  { id: 'scoring', label: 'Scoring' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'data', label: 'Data & Backup' },
]

function GeneralTab() {
  const settings = useSettings()
  if (settings.isPending) return <Skeleton className="h-64 w-full" />
  if (settings.isError) return <p className="text-sm text-red-600">Settings could not be loaded.</p>
  return (
    <div className="space-y-4">
      <GeneralSettingsForm initial={settings.data} />
      <ChangePasswordForm />
    </div>
  )
}

export function SettingsPage() {
  const activeId = useTabParam(tabs.map((tab) => tab.id))
  const active = tabs.find((tab) => tab.id === activeId)!

  return (
    <>
      <PageHeader title="Settings and Job Sources" description="Configure the app, sources, scoring and backups." />
      <Tabs tabs={tabs} activeId={activeId} label="Settings sections" />
      {activeId === 'general' ? (
        <GeneralTab />
      ) : (
        <EmptyState icon={Settings} title={active.label} description="Nothing to show here yet." />
      )}
    </>
  )
}
