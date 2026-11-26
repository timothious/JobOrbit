import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query'
import { ApiError } from './client'
import type { AuthStatus } from './types'

export const authStatusKey = ['auth', 'status'] as const

export function createQueryClient() {
  // Any 401 means the session ended: flip the cached status so the auth guard redirects to login.
  const onError = (error: Error) => {
    if (error instanceof ApiError && error.status === 401) {
      client.setQueryData<AuthStatus>(authStatusKey, (prev) => prev && { ...prev, authenticated: false })
    }
  }

  const client: QueryClient = new QueryClient({
    queryCache: new QueryCache({ onError }),
    mutationCache: new MutationCache({ onError }),
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 2,
      },
    },
  })
  return client
}
