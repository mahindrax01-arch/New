import { useEffect } from 'react'

type SocketMessage = {
  event: string
  payload: Record<string, unknown>
}

function getDefaultWsUrl() {
  if (typeof window === 'undefined') {
    return 'ws://127.0.0.1:8000/ws'
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.hostname}:8000/ws`
}

const WS_URL = import.meta.env.VITE_WS_URL || getDefaultWsUrl()

export function useLiveSocket(accessToken: string | undefined, onMessage: (msg: SocketMessage) => void) {
  useEffect(() => {
    if (!accessToken) return

    const socket = new WebSocket(`${WS_URL}?token=${encodeURIComponent(accessToken)}`)

    socket.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as SocketMessage
        onMessage(msg)
      } catch {
        // Ignore malformed payloads.
      }
    }

    const ping = window.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send('ping')
      }
    }, 30000)

    return () => {
      window.clearInterval(ping)
      socket.close()
    }
  }, [accessToken, onMessage])
}
