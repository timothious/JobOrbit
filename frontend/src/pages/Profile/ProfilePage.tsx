import { useProfile } from '@/api'
import { PageHeader, Skeleton } from '@/components'
import { ProfileForm } from './components/ProfileForm'

export function ProfilePage() {
  const profile = useProfile()

  return (
    <>
      <PageHeader title="My Profile" description="Your citizenships, skills and preferences used for matching." />
      {profile.isPending && <Skeleton className="h-64 w-full" />}
      {profile.isError && <p className="text-sm text-red-600">Profile could not be loaded.</p>}
      {profile.data && <ProfileForm key={profile.data.profile_version} initial={profile.data} />}
    </>
  )
}
