import type { Note } from '../types/note'
const BASE = `${import.meta.env.BASE_URL}api`
export class ApiError extends Error { constructor(message:string, public status:number){super(message)} }
async function request<T>(path:string, init?:RequestInit):Promise<T>{
 try { const response=await fetch(`${BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...init?.headers}}); if(!response.ok) throw new ApiError('Ошибка сервера',response.status); return response.status===204 ? undefined as T : response.json() }
 catch(error){ if(error instanceof ApiError) throw error; throw new ApiError('Нет подключения к серверу',0) }
}
export const api={month:(year:number,month:number)=>request<Note[]>(`/notes?year=${year}&month=${month}`), search:(q:string)=>request<Note[]>(`/notes/search?q=${encodeURIComponent(q)}`), create:(date:string,text:string)=>request<Note>('/notes',{method:'POST',body:JSON.stringify({date,text})}), update:(date:string,text:string)=>request<Note|undefined>(`/notes/${date}`,{method:'PUT',body:JSON.stringify({text})})}
