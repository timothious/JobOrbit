import type { ReactNode } from 'react'

interface AuthLayoutProps {
  title: string
  description: string
  children: ReactNode
}

export function AuthLayout({ title, description, children }: AuthLayoutProps) {
  return (
    <main className="flex min-h-dvh items-center justify-center p-4">
      <title>{`${title} · JobOrbit`}</title>
      <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6">
        <p className="text-base font-semibold text-blue-700">JobOrbit</p>
        <h1 className="mt-4 text-xl font-semibold text-slate-900">{title}</h1>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
        <div className="mt-6">{children}</div>
      </div>
    </main>
  )
}
