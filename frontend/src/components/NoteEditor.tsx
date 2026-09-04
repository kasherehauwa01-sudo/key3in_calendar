import { useEffect, useState } from 'react'
import {
  AppBar,
  Box,
  Button,
  IconButton,
  Paper,
  TextField,
  Toolbar,
  Typography,
} from '@mui/material'
import ArrowBackRounded from '@mui/icons-material/ArrowBackRounded'
import AutorenewRounded from '@mui/icons-material/AutorenewRounded'
import type { Note } from '../types/note'
import { fullDate } from '../utils/date'

type NoteEditorProps = {
  date: string
  initial: string
  notes: Note[]
  userId: number
  userName: string
  userColor: string
  onClose: () => void
  onSave: (text: string) => void
  saving: boolean
}

export function NoteEditor({
  date,
  initial,
  notes,
  userId,
  userName,
  userColor,
  onClose,
  onSave,
  saving,
}: NoteEditorProps) {
  const [text, setText] = useState(initial)
  const otherNotes = notes.filter((note) => note.user_id !== userId || note.recurring)

  useEffect(() => setText(initial), [initial, date])

  const close = () => {
    if (
      text !== initial &&
      !confirm('Закрыть редактор без сохранения изменений?')
    )
      return
    onClose()
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        inset: 0,
        zIndex: 1300,
        bgcolor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
        height: '100dvh',
      }}
    >
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar sx={{ gap: 1 }}>
          <IconButton aria-label="Назад" onClick={close}>
            <ArrowBackRounded />
          </IconButton>
          <Typography
            variant="h6"
            sx={{ fontWeight: 700, flex: 1, fontSize: { xs: '1rem', sm: '1.25rem' } }}
          >
            {fullDate(date)}
          </Typography>
          <Button
            variant="contained"
            disabled={saving}
            onClick={() => onSave(text)}
            sx={{ minWidth: 72 }}
          >
            ОК
          </Button>
        </Toolbar>
      </AppBar>

      <Box
        component="main"
        sx={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          p: 2,
          maxWidth: 900,
          width: '100%',
          mx: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {otherNotes.length > 0 && (
          <Box aria-label="Заметки других пользователей">
            <Typography variant="subtitle2" color="text.secondary" mb={1}>
              Заметки на этот день
            </Typography>
            <Box sx={{ display: 'grid', gap: 1 }}>
              {otherNotes.map((note) => (
                <Paper key={note.id} variant="outlined" sx={{ p: 1.5 }}>
                  <Typography sx={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
                    <Box component="span" sx={{ color: note.user_color, fontWeight: 800 }}>
                      {note.recurring ? <AutorenewRounded fontSize="small" aria-label="Повторяющееся событие" /> : `${note.user_name}:`}{' '}
                    </Box>
                    {note.text}
                  </Typography>
                </Paper>
              ))}
            </Box>
          </Box>
        )}

        <Box sx={{ flex: 1, minHeight: 180, display: 'flex', flexDirection: 'column' }}>
          <Typography sx={{ color: userColor, fontWeight: 800, mb: 1 }}>
            {userName}:
          </Typography>
          <TextField
            autoFocus
            multiline
            fullWidth
            placeholder="Введите заметку... Можно использовать эмодзи 😊"
            value={text}
            onChange={(event) => setText(event.target.value)}
            inputProps={{ maxLength: 20000, 'aria-label': `Заметка пользователя ${userName}` }}
            sx={{
              flex: 1,
              '& .MuiInputBase-root': {
                height: '100%',
                alignItems: 'flex-start',
                bgcolor: 'background.paper',
              },
              '& textarea': { height: '100%!important', overflow: 'auto!important' },
            }}
          />
        </Box>
      </Box>
    </Box>
  )
}
