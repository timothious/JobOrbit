import { describe, expect, it } from 'vitest'
import { findNavItem } from './navigation'

describe('findNavItem', () => {
  it('matches the dashboard only on the root path', () => {
    expect(findNavItem('/')?.label).toBe('Dashboard')
    expect(findNavItem('/unknown')).toBeUndefined()
  })

  it('matches nested routes to their section', () => {
    expect(findNavItem('/jobs/42')?.label).toBe('Jobs')
    expect(findNavItem('/countries/DE/eligibility')?.label).toBe('Countries')
  })

  it('does not match on a shared prefix', () => {
    expect(findNavItem('/jobsearch')).toBeUndefined()
  })
})
