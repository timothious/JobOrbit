import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, setCsrfToken } from './client'
import { authStatusKey } from './queryClient'
import type { AuthStatus, SessionInfo, SetupRequest } from './types'

export function useAuthStatus() {
  return useQuery({ queryKey: authStatusKey, queryFn: () => api<AuthStatus>('GET', '/auth/status') })
}

/** Loads the CSRF token for an existing session (e.g. after a page reload). */
export function useSession(enabled: boolean) {
  return useQuery({
    queryKey: ['auth', 'session'],
    queryFn: async () => {
      const session = await api<SessionInfo>('GET', '/auth/session')
      setCsrfToken(session.csrf_token)
      return session
    },
    enabled,
    staleTime: Infinity,
  })
}

function useSignIn<TBody>(path: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: TBody) => api<SessionInfo>('POST', path, body),
    onSuccess: (session) => {
      setCsrfToken(session.csrf_token)
      queryClient.setQueryData(['auth', 'session'], session)
      queryClient.setQueryData<AuthStatus>(authStatusKey, { setup_complete: true, authenticated: true })
    },
  })
}

export const useLogin = () => useSignIn<{ password: string }>('/auth/login')
export const useSetup = () => useSignIn<SetupRequest>('/auth/setup')

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api<void>('POST', '/auth/logout'),
    onSettled: () => {
      setCsrfToken(null)
      queryClient.clear()
      queryClient.setQueryData<AuthStatus>(authStatusKey, { setup_complete: true, authenticated: false })
    },
  })
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (body: { current_password: string; new_password: string }) =>
      api<void>('POST', '/auth/change-password', body),
  })
}
