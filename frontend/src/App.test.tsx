import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App'

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

afterEach(cleanup)

describe('App routes', () => {
  it('renders the dashboard and sets the document title', async () => {
    renderAt('/')
    expect(await screen.findByRole('heading', { level: 1, name: 'Dashboard' })).toBeTruthy()
    await waitFor(() => expect(document.title).toBe('Dashboard · JobOrbit'))
  })

  it('selects the tab from the query string', async () => {
    renderAt('/settings?tab=sources')
    const tab = await screen.findByRole('link', { name: 'Job Sources' })
    expect(tab.getAttribute('aria-current')).toBe('page')
  })

  it('falls back to the first tab for an unknown tab id', async () => {
    renderAt('/opportunities?tab=nope')
    const tab = await screen.findByRole('link', { name: 'Rankings' })
    expect(tab.getAttribute('aria-current')).toBe('page')
  })

  it('shows the not-found page for unknown routes', async () => {
    renderAt('/does-not-exist')
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeTruthy()
  })
})
