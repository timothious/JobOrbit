import { lazy } from 'react'
import { Route, Routes } from 'react-router'
import { AppShell } from '@/components'

const DashboardPage = lazy(() => import('@/pages/Dashboard').then((m) => ({ default: m.DashboardPage })))
const JobsPage = lazy(() => import('@/pages/Jobs').then((m) => ({ default: m.JobsPage })))
const JobDetailsPage = lazy(() => import('@/pages/JobDetails').then((m) => ({ default: m.JobDetailsPage })))
const CountriesPage = lazy(() => import('@/pages/Countries').then((m) => ({ default: m.CountriesPage })))
const CountryEligibilityPage = lazy(() => import('@/pages/CountryEligibility').then((m) => ({ default: m.CountryEligibilityPage })))
const ApplicationsPage = lazy(() => import('@/pages/Applications').then((m) => ({ default: m.ApplicationsPage })))
const SavedPage = lazy(() => import('@/pages/Saved').then((m) => ({ default: m.SavedPage })))
const ProfilePage = lazy(() => import('@/pages/Profile').then((m) => ({ default: m.ProfilePage })))
const OpportunitiesPage = lazy(() => import('@/pages/Opportunities').then((m) => ({ default: m.OpportunitiesPage })))
const SettingsPage = lazy(() => import('@/pages/Settings').then((m) => ({ default: m.SettingsPage })))
const NotificationsPage = lazy(() => import('@/pages/Notifications').then((m) => ({ default: m.NotificationsPage })))
const NotFoundPage = lazy(() => import('@/pages/NotFound').then((m) => ({ default: m.NotFoundPage })))

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="jobs/:id" element={<JobDetailsPage />} />
        <Route path="countries" element={<CountriesPage />} />
        <Route path="countries/:code" element={<CountriesPage />} />
        <Route path="countries/:code/eligibility" element={<CountryEligibilityPage />} />
        <Route path="applications" element={<ApplicationsPage />} />
        <Route path="applications/:id" element={<ApplicationsPage />} />
        <Route path="saved" element={<SavedPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="opportunities" element={<OpportunitiesPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
