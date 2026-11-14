import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { TelegramSettings } from './TelegramSettings'

afterEach(() => vi.restoreAllMocks())

describe('Telegram settings', () => {
  it('opens the bot link and refreshes the state when returning', async () => {
    const status = vi.spyOn(api, 'telegramStatus').mockResolvedValue({ available: true, connected: false, pending: false })
    const url = 'https://t.me/example_bot?start=example'
    vi.spyOn(api, 'connectTelegram').mockImplementation(async () => {
      status.mockResolvedValue({ available: true, connected: false, pending: true })
      return { url }
    })
    const replace = vi.fn()
    vi.spyOn(window, 'open').mockReturnValue({ opener: window, location: { replace }, closed: false } as unknown as Window)

    render(<TelegramSettings />)
    fireEvent.click(await screen.findByRole('button', { name: 'Подключить Telegram' }))
    expect(await screen.findByText(/нажмите «Запустить»/)).toBeInTheDocument()
    expect(replace).toHaveBeenCalledWith(url)

    status.mockResolvedValue({ available: true, connected: true, pending: false })
    fireEvent.focus(window)
    expect(await screen.findByText('Telegram подключён')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Отключить Telegram' })).toBeInTheDocument()
  })
})
