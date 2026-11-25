import { useSearchParams } from 'react-router'

export function useTabParam(ids: readonly string[]) {
  const [params] = useSearchParams()
  const requested = params.get('tab')
  return requested && ids.includes(requested) ? requested : ids[0]
}
