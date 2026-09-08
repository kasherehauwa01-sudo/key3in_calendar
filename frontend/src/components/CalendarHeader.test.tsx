import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { CalendarHeader } from './CalendarHeader'

afterEach(cleanup)

const renderHeader = (showMonth: boolean, showWeek: boolean) => render(
  <CalendarHeader
    title="Сентябрь 2026"
    showMonth={showMonth}
    showWeek={showWeek}
    hasUnread={false}
    onPrevious={vi.fn()}
    onNext={vi.fn()}
    onToday={vi.fn()}
    onWeek={vi.fn()}
    onSearch={vi.fn()}
    onNotifications={vi.fn()}
    onSettings={vi.fn()}
    onRecurring={vi.fn()}
  />,
)

describe('CalendarHeader', () => {
  it('скрывает переход в уже открытый месячный просмотр', () => {
    renderHeader(true, false)

    expect(screen.queryByRole('button', { name: 'Месячный просмотр' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Недельный просмотр' })).toBeInTheDocument()
  })

  it('скрывает переход в уже открытый недельный просмотр', () => {
    renderHeader(false, true)

    expect(screen.getByRole('button', { name: 'Месячный просмотр' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Недельный просмотр' })).not.toBeInTheDocument()
  })
})
