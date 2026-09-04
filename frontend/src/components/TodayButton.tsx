import { Box,IconButton } from '@mui/material'
import CalendarTodayRounded from '@mui/icons-material/CalendarTodayRounded'
export function TodayButton({onClick}:{onClick:()=>void}){const day=new Date().getDate();return <IconButton aria-label="Сегодня" onClick={onClick} sx={{position:'relative'}}><CalendarTodayRounded/><Box component="span" sx={{position:'absolute',top:20,fontSize:9,fontWeight:900}}>{day}</Box></IconButton>}
