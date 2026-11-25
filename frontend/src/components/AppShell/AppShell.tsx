import { Suspense, useEffect, useRef } from 'react'
import { Outlet, useLocation } from 'react-router'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { Skeleton } from '@/components/Skeleton'
import { BottomNav } from './components/BottomNav'
import { Sidebar } from './components/Sidebar'
import { TopBar } from './components/TopBar'

function PageFallback() {
  return (
    <div className="space-y-3" role="status" aria-label="Loading">
      <Skeleton className="h-7 w-48" />
      <Skeleton className="h-40 w-full" />
    </div>
  )
}

export function AppShell() {
  const { pathname } = useLocation()
  const mainRef = useRef<HTMLElement>(null)
  const firstPath = useRef(pathname)

  // Move focus to the new page on navigation so screen readers announce it.
  useEffect(() => {
    if (pathname !== firstPath.current) mainRef.current?.focus()
  }, [pathname])

  return (
    <div className="flex h-dvh">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:shadow-lg"
      >
        Skip to main content
      </a>
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main id="main" ref={mainRef} tabIndex={-1} className="flex-1 overflow-y-auto p-4 outline-none">
          <ErrorBoundary key={pathname}>
            <Suspense fallback={<PageFallback />}>
              <Outlet />
            </Suspense>
          </ErrorBoundary>
        </main>
        <BottomNav />
      </div>
    </div>
  )
}
