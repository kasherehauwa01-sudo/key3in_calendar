import { render, screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { WeekView } from './WeekView'
import { isoDate, WEEKDAYS } from '../utils/date'

describe('WeekView', () => {
  it('показывает дату над днем недели и выделяет сегодняшний день', () => {
    const now = new Date()
    const weekdayIndex = (now.getDay() + 6) % 7

    render(<WeekView notes={new Map()} onSelect={vi.fn()} />)

    const today = screen.getByRole('button', {
      name: `${WEEKDAYS[weekdayIndex]}, ${now.getDate()}`,
    })
    const labels = within(today).getAllByText(
      new RegExp(`^(${now.getDate()}|${WEEKDAYS[weekdayIndex]})$`),
    )

    expect(today).toHaveStyle({ boxShadow: 'inset 4px 0 0 #425f91' })
    expect(labels[0]).toHaveAttribute('datetime', isoDate(now))
    expect(labels[1]).toHaveTextContent(WEEKDAYS[weekdayIndex])
  })
})
