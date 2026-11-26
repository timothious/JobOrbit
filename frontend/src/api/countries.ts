import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from './client'
import type { CountryDetail, CountryListItem, CountryOption, Page } from './types'

const REFERENCE_STALE_TIME = 5 * 60_000

export function useCountryOptions() {
  return useQuery({
    queryKey: ['countries', 'options'],
    queryFn: () => api<CountryOption[]>('GET', '/countries/options'),
    staleTime: REFERENCE_STALE_TIME,
  })
}

export function useCountries(params: { q: string; page: number }) {
  const search = new URLSearchParams({ page: String(params.page) })
  if (params.q) search.set('q', params.q)
  return useQuery({
    queryKey: ['countries', 'list', params],
    queryFn: () => api<Page<CountryListItem>>('GET', `/countries?${search}`),
    placeholderData: keepPreviousData,
    staleTime: REFERENCE_STALE_TIME,
  })
}

export function useCountry(code: string | undefined) {
  return useQuery({
    queryKey: ['countries', 'detail', code],
    queryFn: () => api<CountryDetail>('GET', `/countries/${code}`),
    enabled: Boolean(code),
    staleTime: REFERENCE_STALE_TIME,
  })
}
