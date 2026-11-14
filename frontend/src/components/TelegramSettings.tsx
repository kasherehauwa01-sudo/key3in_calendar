import { useEffect, useState } from 'react'
import { Box, Button, Typography } from '@mui/material'
import { api, type TelegramStatus } from '../services/api'

function telegramAppUrl(webUrl: string) {
  const url = new URL(webUrl)
  const username = url.pathname.slice(1)
  const start = url.searchParams.get('start')
  if (url.origin !== 'https://t.me' || !/^[A-Za-z0-9_]{5,32}$/.test(username)
    || !start || !/^[A-Za-z0-9_-]{43}$/.test(start)) {
    throw new Error('Не удалось получить ссылку на бота')
  }
  return `tg://resolve?${new URLSearchParams({ domain: username, start })}`
}

export function TelegramSettings() {
  const [status, setStatus] = useState<TelegramStatus>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  const [links, setLinks] = useState<{ web: string; app: string }>()
  const android = /Android/i.test(navigator.userAgent)

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
          if (result.connected || !result.pending || !result.available) setLinks(undefined)
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
    setBusy(true)
    setError('')
    try {
      const { url } = await api.connectTelegram()
      setLinks({ web: url, app: telegramAppUrl(url) })
      setStatus({ available: true, connected: false, pending: true })
    } catch (cause) {
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
      setLinks(undefined)
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
          ? <>
              {links && status.pending && !busy && <>
                <Button component="a" variant="contained" href={android ? links.app : links.web}
                  target={android ? undefined : '_blank'} rel="noopener noreferrer">Открыть Telegram</Button>
                {android && <Button component="a" href={links.web} target="_blank" rel="noopener noreferrer">Открыть в браузере</Button>}
              </>}
              <Button variant="outlined" disabled={busy} onClick={connect}>
                {busy ? 'Готовим ссылку…' : status.pending ? 'Получить новую ссылку' : 'Подключить Telegram'}
              </Button>
            </>
          : !status && error
            ? <Button onClick={() => { setError(''); setReload(value => value + 1) }}>Повторить проверку</Button>
            : null}
    </Box>
  )
}
