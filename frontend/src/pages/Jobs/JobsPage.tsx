import { BriefcaseBusiness } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function JobsPage() {
  return (
    <>
      <PageHeader title="Global Job Explorer" description="Search and filter jobs from every enabled source." />
      <EmptyState
        icon={BriefcaseBusiness}
        title="No jobs yet"
        description="Jobs will appear here after you enable a source and run a sync."
      />
    </>
  )
}
