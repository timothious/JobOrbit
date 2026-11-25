import { Globe2 } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function CountriesPage() {
  return (
    <>
      <PageHeader title="Country Explorer" description="Compare countries by opportunity and pathways." />
      <EmptyState
        icon={Globe2}
        title="No country data yet"
        description="Country scores appear once jobs are synced and your profile is filled in."
      />
    </>
  )
}
