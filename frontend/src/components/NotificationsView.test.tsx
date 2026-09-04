import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { NotificationsView } from './NotificationsView'

const notifications = [
  {note_id:1,date:'2026-09-04',user_id:2,user_name:'Борис',user_color:'#ff0000',text:'Новая заметка',created_at:'',is_read:false},
  {note_id:2,date:'2026-09-03',user_id:3,user_name:'Вера',user_color:'#0000ff',text:'Прочитано',created_at:'',is_read:true},
]

describe('NotificationsView',()=>{
 it('показывает чужие заметки и позволяет прочитать одну или все',()=>{
  const onRead=vi.fn(),onReadAll=vi.fn()
  render(<NotificationsView notifications={notifications} onBack={vi.fn()} onRead={onRead} onReadAll={onReadAll}/>)
  expect(screen.getByText('Новая заметка')).toBeInTheDocument()
  fireEvent.click(screen.getByText('Новая заметка'))
  expect(onRead).toHaveBeenCalledWith(notifications[0])
  fireEvent.click(screen.getByRole('button',{name:'Прочитать все'}))
  expect(onReadAll).toHaveBeenCalledOnce()
 })
})
