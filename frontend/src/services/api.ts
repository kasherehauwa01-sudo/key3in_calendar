import type { AuthResponse, Note, NoteNotification, RecurringEvent, RecurringEventInput, User } from '../types/note'
const BASE = `${import.meta.env.BASE_URL}api`
const TOKEN_KEY = 'key3in-token'
export class ApiError extends Error { constructor(message:string,public status:number){super(message)} }
export const getToken=()=>localStorage.getItem(TOKEN_KEY)
export const setToken=(token:string|null)=>token?localStorage.setItem(TOKEN_KEY,token):localStorage.removeItem(TOKEN_KEY)
async function request<T>(path:string,init?:RequestInit):Promise<T>{try{const token=getToken();const response=await fetch(`${BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`} : {}),...init?.headers}});if(!response.ok){let message='Ошибка сервера';try{message=(await response.json()).detail??message}catch{/* Ответ сервера может быть не JSON. */}throw new ApiError(message,response.status)}return response.status===204?undefined as T:response.json()}catch(error){if(error instanceof ApiError)throw error;throw new ApiError('Нет подключения к серверу',0)}}
export const api={
 register:(login:string,pin:string,name:string)=>request<AuthResponse>('/auth/register',{method:'POST',body:JSON.stringify({login,pin,name})}),
 login:(login:string,pin:string)=>request<AuthResponse>('/auth/login',{method:'POST',body:JSON.stringify({login,pin})}),
 me:()=>request<User>('/users/me'), updateMe:(name:string,color:string)=>request<User>('/users/me',{method:'PUT',body:JSON.stringify({name,color})}),
 recurringEvents:()=>request<RecurringEvent[]>('/recurring-events'),createRecurringEvent:(value:RecurringEventInput)=>request<RecurringEvent>('/recurring-events',{method:'POST',body:JSON.stringify(value)}),updateRecurringEvent:(id:number,value:RecurringEventInput)=>request<RecurringEvent>(`/recurring-events/${id}`,{method:'PUT',body:JSON.stringify(value)}),deleteRecurringEvent:(id:number)=>request<void>(`/recurring-events/${id}`,{method:'DELETE'}),
 month:(year:number,month:number)=>request<Note[]>(`/notes?year=${year}&month=${month}`),date:(date:string)=>request<Note[]>(`/notes/${date}`),search:(q:string)=>request<Note[]>(`/notes/search?q=${encodeURIComponent(q)}`),
 upsert:(date:string,text:string)=>request<Note>(`/notes/${date}`,{method:'PUT',body:JSON.stringify({text})}),remove:(date:string)=>request<undefined>(`/notes/${date}`,{method:'DELETE'}),
 notifications:()=>request<NoteNotification[]>('/notifications'),readNotification:(noteId:number)=>request<undefined>(`/notifications/${noteId}/read`,{method:'PUT'}),readAllNotifications:()=>request<undefined>('/notifications/read-all',{method:'PUT'})}
