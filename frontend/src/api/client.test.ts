import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, setCsrfToken } from './client'

afterEach(() => {
  vi.unstubAllGlobals()
  setCsrfToken(null)
})

describe('api client', () => {
  it('sends the CSRF header on state-changing requests only', async () => {
    const fetchMock = vi.fn(async () => new Response('{}'))
    vi.stubGlobal('fetch', fetchMock)
    setCsrfToken('token-1')

    await api('GET', '/settings')
    await api('PUT', '/settings', { a: 1 })

    const headers = (call: number) => (fetchMock.mock.calls[call] as unknown as [string, RequestInit])[1].headers
    expect(headers(0)).toEqual({})
    expect(headers(1)).toEqual({ 'Content-Type': 'application/json', 'X-JobOrbit-CSRF': 'token-1' })
  })

  it('maps the error envelope to ApiError with field lookup', async () => {
    const body = {
      error: {
        code: 'validation_error',
        message: 'Request validation failed.',
        details: [{ field: 'profile.citizenship_country_codes.0', code: 'string_pattern_mismatch', message: 'Bad code' }],
      },
      request_id: 'abc',
    }
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(body), { status: 422 })))

    const error = await api('POST', '/auth/setup', {}).catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).code).toBe('validation_error')
    expect((error as ApiError).fieldError('profile.citizenship_country_codes')).toBe('Bad code')
    expect((error as ApiError).requestId).toBe('abc')
  })
})
