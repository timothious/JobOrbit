import { cleanup, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { mockApi, renderWithProviders, signedIn } from './test/utils'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('auth guard', () => {
  it('sends a fresh install to setup', async () => {
    mockApi({ 'GET /auth/status': { setup_complete: false, authenticated: false }, 'GET /countries/options': [] })
    renderWithProviders(<App />, '/jobs')
    expect(await screen.findByRole('heading', { name: 'Set up JobOrbit' })).toBeTruthy()
  })

  it('asks for the password and returns to the requested page', async () => {
    let authenticated = false
    const calls = mockApi({
      'GET /auth/status': () => ({ json: { setup_complete: true, authenticated } }),
      'POST /auth/login': () => {
        authenticated = true
        return { json: signedIn['GET /auth/session'] }
      },
      'GET /auth/session': signedIn['GET /auth/session'],
    })
    renderWithProviders(<App />, '/settings?tab=sources')

    const password = await screen.findByLabelText('Password')
    await userEvent.type(password, 'correct horse battery')
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }))

    const tab = await screen.findByRole('link', { name: 'Job Sources' })
    expect(tab.getAttribute('aria-current')).toBe('page')
    expect(calls.find((c) => c.key === 'POST /auth/login')?.body).toEqual({ password: 'correct horse battery' })
  })

  it('shows the server error for a wrong password', async () => {
    mockApi({
      'GET /auth/status': { setup_complete: true, authenticated: false },
      'POST /auth/login': () => ({ status: 401, json: { error: { code: 'invalid_credentials', message: 'Incorrect password.' } } }),
    })
    renderWithProviders(<App />, '/login')
    await userEvent.type(await screen.findByLabelText('Password'), 'nope nope nope')
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    expect(await screen.findByText('Incorrect password.')).toBeTruthy()
  })
})

describe('signed-in routes', () => {
  it('renders the dashboard and sets the document title', async () => {
    mockApi(signedIn)
    renderWithProviders(<App />, '/')
    expect(await screen.findByRole('heading', { level: 1, name: 'Dashboard' })).toBeTruthy()
    await waitFor(() => expect(document.title).toBe('Dashboard · JobOrbit'))
  })

  it('falls back to the first tab for an unknown tab id', async () => {
    mockApi(signedIn)
    renderWithProviders(<App />, '/opportunities?tab=nope')
    const tab = await screen.findByRole('link', { name: 'Rankings' })
    expect(tab.getAttribute('aria-current')).toBe('page')
  })

  it('shows the not-found page for unknown routes', async () => {
    mockApi(signedIn)
    renderWithProviders(<App />, '/does-not-exist')
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeTruthy()
  })

  it('lists countries and opens a country from the URL', async () => {
    mockApi({
      ...signedIn,
      'GET /countries': {
        items: [{ code: 'DE', name: 'Germany', region: 'Europe', subregion: 'Western Europe', currency_code: 'EUR', english_status: 'unknown', english_status_verified_at: null }],
        page: 1,
        page_size: 20,
        total: 1,
        total_pages: 1,
      },
      'GET /countries/DE': {
        code: 'DE', name: 'Germany', iso3: 'DEU', official_name: 'Federal Republic of Germany', region: 'Europe',
        subregion: 'Western Europe', currency_code: 'EUR', languages: ['de'], region_codes: ['EU', 'EEA'],
        english_status: 'unknown', english_status_verified_at: null,
      },
    })
    renderWithProviders(<App />, '/countries/de')
    expect(await screen.findByRole('link', { name: 'Germany' })).toBeTruthy()
    expect(await screen.findByText('Federal Republic of Germany')).toBeTruthy()
    expect(screen.getByText('EU, EEA')).toBeTruthy()
  })
})
