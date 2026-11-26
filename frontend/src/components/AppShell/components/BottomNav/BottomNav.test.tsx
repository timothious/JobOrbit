import { cleanup, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import { renderWithProviders } from '@/test/utils'
import { BottomNav } from './BottomNav'

function renderAt(path: string) {
  renderWithProviders(<BottomNav />, path)
  return screen.getByRole('button', { name: 'More' })
}

afterEach(cleanup)

describe('BottomNav', () => {
  it('highlights More when a page in its menu is active', () => {
    expect(renderAt('/settings').className).toContain('text-blue-700')
  })

  it('does not highlight More on a primary page', () => {
    expect(renderAt('/jobs').className).not.toContain('text-blue-700')
  })

  it('closes the menu on Escape and on an outside click', async () => {
    const user = userEvent.setup()
    const more = renderAt('/')

    await user.click(more)
    expect(more.getAttribute('aria-expanded')).toBe('true')
    await user.keyboard('{Escape}')
    expect(more.getAttribute('aria-expanded')).toBe('false')

    await user.click(more)
    await user.click(document.body)
    expect(more.getAttribute('aria-expanded')).toBe('false')
  })
})
