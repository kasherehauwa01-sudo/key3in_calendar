import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { TelegramSettings } from './TelegramSettings'

afterEach(() => vi.restoreAllMocks())

const start = 'a'.repeat(43)
const url = `https://t.me/example_bot?start=${start}`

function prepareLink() {
  const status = vi.spyOn(api, 'telegramStatus').mockResolvedValue({ available: true, connected: false, pending: false })
  vi.spyOn(api, 'connectTelegram').mockImplementation(async () => {
    status.mockResolvedValue({ available: true, connected: false, pending: true })
    return { url }
  })
  return status
}

describe('Telegram settings', () => {
  it('offers a normal web link on desktop and refreshes the state when returning', async () => {
    const status = prepareLink()
    const open = vi.spyOn(window, 'open').mockReturnValue(null)

    render(<TelegramSettings />)
    fireEvent.click(await screen.findByRole('button', { name: 'Подключить Telegram' }))
    expect(await screen.findByRole('link', { name: 'Открыть Telegram' })).toHaveAttribute('href', url)
    expect(open).not.toHaveBeenCalled()

    status.mockResolvedValue({ available: true, connected: true, pending: false })
    fireEvent.focus(window)
    expect(await screen.findByText('Telegram подключён')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Открыть Telegram' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Отключить Telegram' })).toBeInTheDocument()
  })

  it('offers a native Android link with the same token and a browser fallback', async () => {
    vi.spyOn(window.navigator, 'userAgent', 'get').mockReturnValue('Mozilla/5.0 (Linux; Android 15)')
    prepareLink()
    render(<TelegramSettings />)

    fireEvent.click(await screen.findByRole('button', { name: 'Подключить Telegram' }))
    expect(await screen.findByRole('link', { name: 'Открыть Telegram' }))
      .toHaveAttribute('href', `tg://resolve?domain=example_bot&start=${start}`)
    expect(screen.getByRole('link', { name: 'Открыть в браузере' })).toHaveAttribute('href', url)
  })
})
