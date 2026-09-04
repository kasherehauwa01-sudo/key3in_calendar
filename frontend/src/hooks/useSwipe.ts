import { useRef } from 'react'
export function useSwipe(onLeft:()=>void,onRight:()=>void){
 const start=useRef<{x:number;y:number}|null>(null)
 return {onPointerDown:(e:React.PointerEvent)=>{start.current={x:e.clientX,y:e.clientY}},onPointerUp:(e:React.PointerEvent)=>{if(!start.current)return;const dx=e.clientX-start.current.x,dy=e.clientY-start.current.y;start.current=null;if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.4)(dx<0?onLeft:onRight)()}}
}
