import { FileSearch } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function JobDetailsPage() {
  return (
    <>
      <PageHeader title="Job Details" description="Full listing, eligibility and application actions." />
      <EmptyState
        icon={FileSearch}
        title="Job not found"
        description="Open a job from the Jobs list to see its details."
      />
    </>
  )
}
