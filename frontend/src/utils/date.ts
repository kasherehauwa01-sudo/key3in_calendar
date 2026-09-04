export const WEEKDAYS = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
export const isoDate = (date: Date) => `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
export const parseDate = (value:string) => { const [y,m,d]=value.split('-').map(Number); return new Date(y,m-1,d) }
export const monthKey = (date:Date) => `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}`
export const monthTitle = (date:Date) => { const value=new Intl.DateTimeFormat('ru-RU',{month:'long',year:'numeric'}).format(date); return value[0].toUpperCase()+value.slice(1) }
export const fullDate = (value:string) => new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'long',year:'numeric'}).format(parseDate(value))
export const shiftMonth = (date:Date, amount:number) => new Date(date.getFullYear(),date.getMonth()+amount,1)
export interface CalendarCell { date:string; day:number; currentMonth:boolean }
export function buildCalendar(date:Date):CalendarCell[]{
 const first=new Date(date.getFullYear(),date.getMonth(),1); const mondayOffset=(first.getDay()+6)%7; const start=new Date(date.getFullYear(),date.getMonth(),1-mondayOffset)
 return Array.from({length:42},(_,i)=>{const d=new Date(start.getFullYear(),start.getMonth(),start.getDate()+i);return {date:isoDate(d),day:d.getDate(),currentMonth:d.getMonth()===date.getMonth()}})
}
