import { KanbanSquare } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function ApplicationsPage() {
  return (
    <>
      <PageHeader title="Application Tracker" description="Track every application from saved to outcome." />
      <EmptyState
        icon={KanbanSquare}
        title="No applications yet"
        description="Applications you add will be tracked here."
      />
    </>
  )
}
