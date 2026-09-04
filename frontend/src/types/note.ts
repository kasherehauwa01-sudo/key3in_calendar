export interface Note { id:number; date:string; user_id:number; user_name:string; user_color:string; text:string; created_at:string; updated_at:string; cache_key?:string }
export interface User { id:number; login:string; name:string; color:string }
export interface AuthResponse { token:string; user:User }
