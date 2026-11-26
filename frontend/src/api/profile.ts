import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { Profile, ProfilePatch } from './types'

const key = ['profile'] as const

export function useProfile() {
  return useQuery({ queryKey: key, queryFn: () => api<Profile>('GET', '/profile') })
}

export function useUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (patch: ProfilePatch) => api<Profile>('PATCH', '/profile', patch),
    onSuccess: (saved) => queryClient.setQueryData(key, saved),
  })
}
