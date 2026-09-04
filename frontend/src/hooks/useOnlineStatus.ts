import { useEffect, useState } from 'react'

export function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(() => navigator.onLine)
  useEffect(() => {
    const enable = () => setOnline(true)
    const disable = () => setOnline(false)
    window.addEventListener('online', enable)
    window.addEventListener('offline', disable)
    return () => {
      window.removeEventListener('online', enable)
      window.removeEventListener('offline', disable)
    }
  }, [])
  return online
}
