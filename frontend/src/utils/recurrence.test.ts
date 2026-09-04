import {describe,expect,it} from 'vitest'
import {recurringNotes} from './recurrence'
import type {RecurringEvent} from '../types/note'
describe('график повторяющегося события',()=>{it('чередует x дней события и y дней пропуска',()=>{const event:RecurringEvent={id:1,user_id:1,user_name:'Анна',user_color:'#000000',text:'Смена',start_date:'2026-09-01',interval:1,unit:'day',weekdays:[],end_date:null,count:null,active_days:2,rest_days:3};expect(recurringNotes([event],'2026-09').slice(0,6).map(note=>note.date)).toEqual(['2026-09-01','2026-09-02','2026-09-06','2026-09-07','2026-09-11','2026-09-12'])})})
