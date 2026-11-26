import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { AppSettings } from './types'

const key = ['settings'] as const

export function useSettings() {
  return useQuery({ queryKey: key, queryFn: () => api<AppSettings>('GET', '/settings') })
}

export function useSaveSettings() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (settings: AppSettings) => api<AppSettings>('PUT', '/settings', settings),
    onSuccess: (saved) => queryClient.setQueryData(key, saved),
  })
}
