import { render, screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { WeekView } from './WeekView'
import type { Note } from '../types/note'
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

  it('размещает дату, заметки и повторы в отдельных колонках', () => {
    const today = isoDate(new Date())
    const notes = new Map<string, Note[]>([
      [today, [
        {id:1,date:today,user_id:1,user_name:'Анна',user_color:'#000',text:'Обычная заметка',created_at:'',updated_at:''},
        {id:2,date:today,user_id:1,user_name:'Анна',user_color:'#000',text:'Повтор',created_at:'',updated_at:'',recurring:true},
      ]],
    ])

    render(<WeekView notes={notes} onSelect={vi.fn()} />)

    expect(screen.getByText('Обычная заметка').closest('[aria-label="Заметки"]')).toBeInTheDocument()
    expect(screen.getByText('Повтор').closest('[aria-label="Повторяющиеся события"]')).toBeInTheDocument()
  })
})
