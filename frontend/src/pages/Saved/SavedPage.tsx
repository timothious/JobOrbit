import { Bookmark } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function SavedPage() {
  return (
    <>
      <PageHeader title="Saved Jobs" description="Jobs you have bookmarked." />
      <EmptyState
        icon={Bookmark}
        title="No saved jobs"
        description="Save a job from the Jobs list to find it here."
      />
    </>
  )
}
