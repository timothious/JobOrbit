import { PageHeader } from '@/components'
import { FirstRunChecklist } from './components/FirstRunChecklist'

export function DashboardPage() {
  return (
    <>
      <PageHeader title="Dashboard" description="Daily overview of jobs and applications." />
      <FirstRunChecklist />
    </>
  )
}
