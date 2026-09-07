import { useEffect, useState } from 'react'
import { Box, CircularProgress, IconButton, List, ListItemButton, ListItemText, TextField, Typography } from '@mui/material'
import ArrowBackRounded from '@mui/icons-material/ArrowBackRounded'
import { api } from '../services/api'
import { cacheNotes, getPendingChanges, searchCachedNotes } from '../services/offlineStore'
import type { Note, RecurringEvent } from '../types/note'
import { fullDate } from '../utils/date'

interface SearchViewProps {
  query: string
  setQuery: (value: string) => void
  online: boolean
  userId: number
  recurring: RecurringEvent[]
  onClose: () => void
  onSelect: (note: Note) => void
  onError: (message: string) => void
}

export function SearchView({ query, setQuery, online, userId, recurring, onClose, onSelect, onError }: SearchViewProps) {
  const [results, setResults] = useState<Note[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      setLoading(false)
      return
    }
    let active = true
    const timer = setTimeout(async () => {
      setLoading(true)
      const normalized=query.trim().toLocaleLowerCase('ru-RU'),recurringFound=recurring.filter(event=>event.text.toLocaleLowerCase('ru-RU').includes(normalized)).map(event=>({id:-event.id,date:event.start_date,user_id:event.user_id,user_name:event.user_name,user_color:event.user_color,text:event.text,created_at:'',updated_at:'',recurring:true} satisfies Note))
      try {
        let found: Note[]
        if (online) {
          const [remote, cached, pending] = await Promise.all([
            api.search(query.trim()),
            searchCachedNotes(userId, query.trim()),
            getPendingChanges(userId),
          ])
          const pendingDates = new Set(pending.map(change => change.date))
          await cacheNotes(remote.filter(note => !pendingDates.has(note.date)))
          found = [...remote.filter(note => !pendingDates.has(note.date)), ...cached]
            .filter((note, index, all) => all.findIndex(item => item.date === note.date) === index)
            .sort((a, b) => a.date.localeCompare(b.date))
        } else {
          found = await searchCachedNotes(userId, query.trim())
        }
        if (active) setResults([...found,...recurringFound].sort((a,b)=>a.date.localeCompare(b.date)))
      } catch (error) {
        try {
          const cached = await searchCachedNotes(userId, query.trim())
          if (active) setResults([...cached,...recurringFound].sort((a,b)=>a.date.localeCompare(b.date)))
        } catch {
          onError(error instanceof Error ? error.message : 'Ошибка поиска')
        }
      } finally {
        if (active) setLoading(false)
      }
    }, 300)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [query, online, userId, recurring, onError])

  return <Box sx={{flex:1,minHeight:0,overflowY:'auto'}}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 1 }}>
      <IconButton aria-label="Закрыть поиск" onClick={onClose}><ArrowBackRounded /></IconButton>
      <TextField autoFocus fullWidth size="small" placeholder="Поиск заметок" value={query} onChange={event => setQuery(event.target.value)} inputProps={{ 'aria-label': 'Поиск заметок' }} />
    </Box>
    {loading && <Box textAlign="center" p={3}><CircularProgress size={28} /></Box>}
    {!query.trim() && <Typography color="text.secondary" textAlign="center" p={4}>Введите текст для поиска заметок</Typography>}
    {query.trim() && !loading && !results.length && <Typography color="text.secondary" textAlign="center" p={4}>Ничего не найдено</Typography>}
    <List>{results.map(note => <ListItemButton key={`${note.date}-${note.id}`} onClick={() => onSelect(note)} sx={{ borderRadius: 3, mb: 1, bgcolor: 'background.paper' }}>
      <ListItemText primary={fullDate(note.date)} secondary={note.text} primaryTypographyProps={{ fontWeight: 700 }} secondaryTypographyProps={{ sx: { display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' } }} />
    </ListItemButton>)}</List>
  </Box>
}
