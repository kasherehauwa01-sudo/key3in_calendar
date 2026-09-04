export interface Note { id:number; date:string; user_id:number; user_name:string; user_color:string; text:string; created_at:string; updated_at:string; cache_key?:string; recurring?:boolean }
export interface User { id:number; login:string; name:string; color:string }
export interface AuthResponse { token:string; user:User }
export interface NoteNotification { note_id:number; date:string; user_id:number; user_name:string; user_color:string; text:string; created_at:string; is_read:boolean }
export interface RecurringEvent {id:number;user_id:number;user_name:string;user_color:string;text:string;start_date:string;interval:number;unit:'day'|'week'|'month'|'year';weekdays:number[];end_date:string|null;count:number|null}
export type RecurringEventInput=Omit<RecurringEvent,'id'|'user_id'|'user_name'|'user_color'>
