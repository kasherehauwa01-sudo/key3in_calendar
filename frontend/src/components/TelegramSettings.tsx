import { useEffect, useState } from 'react'
import { Box, Button, Typography } from '@mui/material'
import { api, type TelegramStatus } from '../services/api'

export function TelegramSettings() {
  const [status, setStatus] = useState<TelegramStatus>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)

  const pending = status?.pending ?? false
  const loaded = status !== undefined

  useEffect(() => {
    if (busy) return
    let active = true
    let inFlight = false
    const refresh = async () => {
      if (inFlight || document.visibilityState === 'hidden') return
      inFlight = true
      try {
        const result = await api.telegramStatus()
        if (active) {
          setStatus(result)
          if (!loaded) setError('')
        }
      } catch (cause) {
        if (active && !loaded) setError(cause instanceof Error ? cause.message : 'Не удалось проверить Telegram')
      } finally {
        inFlight = false
      }
    }
    void refresh()
    window.addEventListener('focus', refresh)
    document.addEventListener('visibilitychange', refresh)
    const timer = pending ? window.setInterval(refresh, 3000) : undefined
    return () => {
      active = false
      window.removeEventListener('focus', refresh)
      document.removeEventListener('visibilitychange', refresh)
      if (timer !== undefined) window.clearInterval(timer)
    }
  }, [busy, loaded, pending, reload])

  const connect = async () => {
    const tab = window.open('about:blank', '_blank')
    if (tab) tab.opener = null
    setBusy(true)
    setError('')
    try {
      const { url } = await api.connectTelegram()
      if (tab && !tab.closed) tab.location.replace(url)
      else window.location.assign(url)
      setStatus({ available: true, connected: false, pending: true })
    } catch (cause) {
      tab?.close()
      setError(cause instanceof Error ? cause.message : 'Не удалось подключить Telegram')
    } finally {
      setBusy(false)
    }
  }

  const disconnect = async () => {
    setBusy(true)
    setError('')
    try {
      await api.disconnectTelegram()
      setStatus(current => current && { ...current, connected: false, pending: false })
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось отключить Telegram')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Box component="section" aria-labelledby="telegram-settings-title" sx={{ borderTop: 1, borderColor: 'divider', pt: 2, display: 'grid', gap: 1 }}>
      <Typography component="h2" fontWeight={700} id="telegram-settings-title">Telegram</Typography>
      <Typography color="text.secondary">Уведомления о событиях, добавленных другими пользователями.</Typography>
      <Typography role="status" color={status?.connected ? 'success.main' : 'text.secondary'}>
        {status?.connected ? 'Telegram подключён'
          : status?.pending ? 'Откройте бота и нажмите «Запустить» (Start). Не пересылайте ссылку другим.'
          : status ? status.available ? 'Telegram не подключён' : 'Подключение пока недоступно'
          : error ? 'Статус Telegram недоступен' : 'Проверяем подключение…'}
      </Typography>
      {error && <Typography role="alert" color="error">{error}</Typography>}
      {status?.connected
        ? <Button variant="outlined" disabled={busy} onClick={disconnect}>Отключить Telegram</Button>
        : status?.available
          ? <Button variant="outlined" disabled={busy} onClick={connect}>{status.pending ? 'Открыть новую ссылку' : 'Подключить Telegram'}</Button>
          : !status && error
            ? <Button onClick={() => { setError(''); setReload(value => value + 1) }}>Повторить проверку</Button>
            : null}
    </Box>
  )
}
