import { Box, ButtonBase, Typography } from '@mui/material'
import type { Note } from '../types/note'
import { isoDate, WEEKDAYS } from '../utils/date'

const VISIBLE_DAYS = 7
const RENDERED_DAYS = 42

export function WeekView({
  notes,
  onSelect,
}: {
  notes: Map<string, Note[]>
  onSelect: (date: string) => void
}) {
  const now = new Date()
  const monday = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate() - ((now.getDay() + 6) % 7),
  )
  const days = Array.from(
    { length: RENDERED_DAYS },
    (_, index) =>
      new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + index),
  )
  const today = isoDate(now)

  return (
    <Box
      role="grid"
      aria-label="Дни начиная с текущей недели"
      sx={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        display: 'grid',
        gridTemplateColumns: 'minmax(0,1fr)',
        gridAutoRows: `calc((100% - ${VISIBLE_DAYS - 1}px) / ${VISIBLE_DAYS})`,
        gap: '1px',
        bgcolor: 'divider',
      }}
    >
      {days.map((day, index) => {
        const date = isoDate(day)
        const isToday = date === today
        const dayNotes = notes.get(date) ?? []
        const userNotes = dayNotes.filter((note) => !note.recurring)
        const recurringNotes = dayNotes.filter((note) => note.recurring)

        return (
          <ButtonBase
            key={date}
            onClick={() => onSelect(date)}
            aria-label={`${WEEKDAYS[index % 7]}, ${day.getDate()}`}
            sx={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0,4fr) minmax(0,1fr)',
              alignItems: 'stretch',
              textAlign: 'left',
              p: 0,
              borderRadius: 0,
              bgcolor: 'common.white',
              boxShadow: isToday ? 'inset 4px 0 0 #425f91' : 'none',
              overflow: 'hidden',
            }}
          >
            <Box sx={{p:{xs:.75,sm:1},minWidth:0,overflow:'hidden'}}>
              <Box sx={{display:'flex',flexDirection:'column',alignItems:'flex-start',mb:.4}}>
                <Typography component="time" dateTime={date} fontWeight={900} color={isToday ? 'primary.main' : 'text.primary'}>
                  {day.getDate()}
                </Typography>
                <Typography variant="caption" fontWeight={800} color={index % 7 > 4 ? 'error.main' : 'text.secondary'}>
                  {WEEKDAYS[index % 7]}
                </Typography>
              </Box>
              {userNotes.map((note) => (
                <Typography key={note.id} sx={{fontSize:{xs:'.68rem',sm:'.78rem'},whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>
                  <Box component="span" sx={{color:note.user_color,fontWeight:800}}>{note.user_name}:{' '}</Box>
                  {note.text}
                </Typography>
              ))}
            </Box>
            <Box sx={{p:{xs:.75,sm:1},minWidth:0,overflow:'hidden',textAlign:'right'}}>
              {recurringNotes.map((note) => (
                <Typography key={note.id} sx={{fontSize:{xs:'.62rem',sm:'.78rem'},whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>
                  {note.text}
                </Typography>
              ))}
            </Box>
          </ButtonBase>
        )
      })}
    </Box>
  )
}
