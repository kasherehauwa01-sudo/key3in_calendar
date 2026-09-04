import { Box, Button, IconButton, List, ListItemButton, ListItemText, Typography } from '@mui/material'
import ArrowBackRounded from '@mui/icons-material/ArrowBackRounded'
import type { NoteNotification } from '../types/note'
import { fullDate } from '../utils/date'

export function NotificationsView({notifications,onBack,onRead,onReadAll}:{notifications:NoteNotification[];onBack:()=>void;onRead:(notification:NoteNotification)=>void;onReadAll:()=>void}){
 return <Box sx={{flex:1,minHeight:0,overflowY:'auto'}}>
  <Box sx={{display:'flex',alignItems:'center',gap:1,py:1}}><IconButton aria-label="Назад" onClick={onBack}><ArrowBackRounded/></IconButton><Typography variant="h5" fontWeight={700} sx={{flex:1}}>Уведомления</Typography><Button disabled={!notifications.some(item=>!item.is_read)} onClick={onReadAll}>Прочитать все</Button></Box>
  {!notifications.length&&<Typography color="text.secondary" textAlign="center" p={4}>Новых заметок пока нет</Typography>}
  <List>{notifications.map(item=><ListItemButton key={item.note_id} onClick={()=>onRead(item)} sx={{borderRadius:3,mb:1,bgcolor:'background.paper'}}><ListItemText primary={<><Box component="span" sx={{color:item.user_color,fontWeight:item.is_read?400:800}}>{item.user_name}: </Box>{item.text}</>} secondary={fullDate(item.date)} primaryTypographyProps={{fontWeight:item.is_read?400:800,sx:{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}}/></ListItemButton>)}</List>
 </Box>
}
