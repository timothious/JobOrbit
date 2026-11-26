import { QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { vi } from 'vitest'
import { createQueryClient } from '@/api'

type Handler = (body: unknown) => { status?: number; json?: unknown }

/** Stubs `fetch` for `/api/v1` calls. Keys are "METHOD /path" (query string ignored). */
export function mockApi(routes: Record<string, Handler | object>) {
  const calls: { key: string; body: unknown }[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const path = url.replace('/api/v1', '').split('?')[0]
      const key = `${init?.method ?? 'GET'} ${path}`
      const body = init?.body ? JSON.parse(init.body as string) : undefined
      calls.push({ key, body })
      const route = routes[key]
      if (!route) return new Response(JSON.stringify({ error: { code: 'not_found', message: key } }), { status: 404 })
      const result = typeof route === 'function' ? (route as Handler)(body) : { json: route }
      return new Response(result.json === undefined ? null : JSON.stringify(result.json), {
        status: result.status ?? 200,
      })
    }),
  )
  return calls
}

export const signedIn = {
  'GET /auth/status': { setup_complete: true, authenticated: true },
  'GET /auth/session': { csrf_token: 'csrf-1', expires_at: '2026-12-26T09:00:00Z' },
}

export function renderWithProviders(ui: ReactNode, path = '/') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[path]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}
