import { describe, expect, it } from 'vitest'
import { safeNext } from './safeNext'

describe('safeNext', () => {
  it('keeps in-app paths', () => {
    expect(safeNext('/settings?tab=sources')).toBe('/settings?tab=sources')
  })

  it.each([null, '', 'https://evil.example', '//evil.example', 'javascript:alert(1)'])('rejects %s', (next) => {
    expect(safeNext(next)).toBe('/')
  })
})
