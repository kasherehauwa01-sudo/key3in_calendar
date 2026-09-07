import { useRef } from 'react'
import { Box, ButtonBase, Skeleton, Typography } from '@mui/material'
import AutorenewRounded from '@mui/icons-material/AutorenewRounded'
import type { CalendarCell } from '../utils/date'
import type { Note } from '../types/note'

type CalendarDayProps = {
  cell: CalendarCell
  notes: Note[]
  loading: boolean
  highlight: boolean
  today: boolean
  onClick: () => void
  onPreview: (notes: Note[] | null) => void
}

export function CalendarDay({
  cell,
  notes,
  loading,
  highlight,
  today,
  onClick,
  onPreview,
}: CalendarDayProps) {
  const timer=useRef<number|undefined>(undefined),previewing=useRef(false),skipClick=useRef(false)
  const stopPreview=()=>{clearTimeout(timer.current);if(previewing.current){previewing.current=false;onPreview(null)}}
  const weekend = [0, 6].includes(new Date(`${cell.date}T12:00:00`).getDay())
  return (
    <ButtonBase
      id={`day-${cell.date}`}
      aria-label={`${cell.day}${notes.length ? `, заметок: ${notes.length}` : ''}`}
      onPointerDown={event=>{event.currentTarget.setPointerCapture(event.pointerId);previewing.current=false;skipClick.current=false;timer.current=window.setTimeout(()=>{previewing.current=true;skipClick.current=true;onPreview(notes)},1000)}}
      onPointerUp={stopPreview}
      onPointerCancel={stopPreview}
      onContextMenu={event=>event.preventDefault()}
      onClick={()=>{if(skipClick.current){skipClick.current=false;return}onClick()}}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        justifyContent: 'flex-start',
        textAlign: 'left',
        minWidth: 0,
        minHeight: 0,
        height: '100%',
        touchAction: 'none',
        p: { xs: 0.45, sm: 1 },
        borderRadius: 0,
        bgcolor: 'common.white',
        color: cell.currentMonth ? 'text.primary' : 'text.disabled',
        border: '1px solid',
        borderColor: highlight ? 'primary.main' : 'divider',
        '&:focus-visible': {
          outline: '3px solid #425f91',
          outlineOffset: 1,
        },
      }}
    >
      <Typography
        component="span"
        sx={{
          fontWeight: today ? 900 : 700,
          fontSize: { xs: '.78rem', sm: '.95rem' },
          color: today ? 'common.white' : weekend ? 'error.main' : 'inherit',
          opacity: cell.currentMonth ? 1 : .45,
          bgcolor: today ? 'common.black' : 'transparent',
          borderRadius: 1,
          px: .55,
          py: .1,
        }}
      >
        {cell.day}
      </Typography>

      {loading && cell.currentMonth ? (
        <Skeleton width="85%" height={12} />
      ) : (
        <Box sx={{ width: '100%', overflow: 'hidden' }}>
          {notes.map((note) => (
            <Typography
              key={note.id}
              sx={{
                fontSize: { xs: '.52rem', sm: '.72rem' },
                lineHeight: 1.18,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                overflowWrap: 'anywhere',
              }}
            >
              <Box
                component="span"
                sx={{
                  color: note.user_color,
                  fontWeight: 800,
                }}
              >
                {note.recurring ? '•' : `${note.user_name}:`}{' '}
              </Box>
              {note.text}
            </Typography>
          ))}
        </Box>
      )}
    </ButtonBase>
  )
}
