import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router'
import { useAuthStatus, useSession } from '@/api'
import { Skeleton } from '@/components/Skeleton'

function FullPageLoading() {
  return (
    <div className="flex h-dvh items-center justify-center p-4" role="status" aria-label="Loading">
      <Skeleton className="h-10 w-48" />
    </div>
  )
}

/** Sends the visitor to setup or login (keeping the requested URL) until a session exists. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const location = useLocation()
  const status = useAuthStatus()
  const session = useSession(status.data?.authenticated === true)

  if (status.isPending) return <FullPageLoading />
  if (status.isError) {
    return <p className="p-4 text-sm text-red-600">Cannot reach the JobOrbit server. Check that it is running.</p>
  }
  if (!status.data.setup_complete) return <Navigate to="/setup" replace />
  if (!status.data.authenticated) {
    const next = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?next=${next}`} replace />
  }
  if (session.isPending) return <FullPageLoading />
  return children
}
