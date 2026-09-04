import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { NoteEditor } from './NoteEditor'

describe('NoteEditor', () => {
  it('показывает имя текущего пользователя и заметки остальных пользователей', () => {
    render(
      <NoteEditor
        date="2026-09-04"
        initial="Моя заметка 😊"
        notes={[
          {
            id: 1,
            date: '2026-09-04',
            user_id: 1,
            user_name: 'Анна',
            user_color: '#0000ff',
            text: 'Моя заметка 😊',
            created_at: '',
            updated_at: '',
          },
          {
            id: 2,
            date: '2026-09-04',
            user_id: 2,
            user_name: 'Борис',
            user_color: '#ff0000',
            text: 'Общая заметка',
            created_at: '',
            updated_at: '',
          },
        ]}
        userId={1}
        userName="Анна"
        userColor="#0000ff"
        onClose={vi.fn()}
        onSave={vi.fn()}
        saving={false}
      />,
    )

    expect(screen.getByText('Анна:')).toBeInTheDocument()
    expect(screen.getByText('Борис:')).toBeInTheDocument()
    expect(screen.getByText('Общая заметка')).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Заметка пользователя Анна' })).toHaveValue(
      'Моя заметка 😊',
    )
  })
})
