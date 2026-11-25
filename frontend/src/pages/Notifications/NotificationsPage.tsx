import { Bell } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function NotificationsPage() {
  return (
    <>
      <PageHeader title="Notifications" description="Alerts about jobs, deadlines and source health." />
      <EmptyState
        icon={Bell}
        title="You're all caught up"
        description="New notifications will appear here."
      />
    </>
  )
}
