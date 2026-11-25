import { UserRound } from 'lucide-react'
import { EmptyState, PageHeader } from '@/components'

export function ProfilePage() {
  return (
    <>
      <PageHeader title="My Profile" description="Your citizenships, skills and preferences used for matching." />
      <EmptyState
        icon={UserRound}
        title="Profile is empty"
        description="Complete your profile to enable personalised matching."
      />
    </>
  )
}
