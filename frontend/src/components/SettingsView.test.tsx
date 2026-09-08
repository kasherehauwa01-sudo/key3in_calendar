import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { SettingsView } from './SettingsView'

describe('SettingsView', () => {
  it('позволяет выбрать крупный размер шрифта', () => {
    const onFontScaleChange = vi.fn()

    render(
      <SettingsView
        user={{ id: 1, login: 'maria', name: 'Мария', color: '#425f91' }}
        fontScale={112.5}
        onFontScaleChange={onFontScaleChange}
        onBack={vi.fn()}
        onSave={vi.fn()}
        onLogout={vi.fn()}
        onMessage={vi.fn()}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Очень крупный' }))

    expect(onFontScaleChange).toHaveBeenCalledWith(125)
    expect(screen.getByRole('button', { name: 'Мелкий' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Очень мелкий' })).toBeInTheDocument()
  })
})
