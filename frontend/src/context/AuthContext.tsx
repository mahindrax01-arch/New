import { useCallback, useEffect, useMemo, useState } from 'react'

import { apiRequest } from '../api/client'
import { AuthContext } from './auth-context'
import type { AuthTokens, User } from '../types'

const TOKEN_KEY = 'social_tokens'

function readStoredTokens(): AuthTokens | null {
  const raw = localStorage.getItem(TOKEN_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthTokens
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [tokens, setTokens] = useState<AuthTokens | null>(() => readStoredTokens())
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const persistTokens = useCallback((next: AuthTokens | null) => {
    setTokens(next)
    if (next) localStorage.setItem(TOKEN_KEY, JSON.stringify(next))
    else localStorage.removeItem(TOKEN_KEY)
  }, [])

  const clearSession = useCallback(() => {
    persistTokens(null)
    setUser(null)
  }, [persistTokens])

  const loadMe = useCallback(async (accessToken: string) => {
    const me = await apiRequest<User>('/auth/me', { method: 'GET' }, accessToken)
    setUser(me)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const next = await apiRequest<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    persistTokens(next)
    await loadMe(next.access_token)
  }, [loadMe, persistTokens])

  const register = useCallback(async (email: string, username: string, password: string) => {
    await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    })
    await login(email, password)
  }, [login])

  const refreshTokens = useCallback(async () => {
    if (!tokens?.refresh_token) return
    try {
      const next = await apiRequest<AuthTokens>('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      })
      persistTokens(next)
    } catch {
      clearSession()
      throw new Error('Session expired')
    }
  }, [clearSession, persistTokens, tokens?.refresh_token])

  const logout = useCallback(async () => {
    if (tokens?.refresh_token) {
      await apiRequest('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      }).catch(() => undefined)
    }
    clearSession()
  }, [clearSession, tokens?.refresh_token])

  const reloadUser = useCallback(async () => {
    if (!tokens?.access_token) return
    await loadMe(tokens.access_token)
  }, [loadMe, tokens?.access_token])

  useEffect(() => {
    let alive = true

    async function bootstrap() {
      if (!tokens?.access_token) {
        setLoading(false)
        return
      }
      try {
        await loadMe(tokens.access_token)
      } catch {
        clearSession()
      } finally {
        if (alive) setLoading(false)
      }
    }

    bootstrap()

    return () => {
      alive = false
    }
  }, [clearSession, loadMe, tokens?.access_token])

  useEffect(() => {
    if (!tokens?.refresh_token) return

    const id = window.setInterval(() => {
      refreshTokens().catch(() => undefined)
    }, 1000 * 60 * 10)

    return () => window.clearInterval(id)
  }, [refreshTokens, tokens?.refresh_token])

  const value = useMemo(
    () => ({ user, tokens, loading, login, register, logout, refreshTokens, reloadUser, clearSession }),
    [user, tokens, loading, login, register, logout, refreshTokens, reloadUser, clearSession]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
