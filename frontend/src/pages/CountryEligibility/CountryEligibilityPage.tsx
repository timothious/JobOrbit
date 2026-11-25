import { ShieldCheck } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function CountryEligibilityPage() {
  return (
    <>
      <PageHeader title="Country Eligibility Details" description="Pathways and evidence for one country." />
      <EmptyState
        icon={ShieldCheck}
        title="No eligibility data yet"
        description="Add immigration pathways and evidence to see eligibility details."
      />
    </>
  )
}
