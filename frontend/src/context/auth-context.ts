import { createContext } from 'react'

import type { AuthTokens, User } from '../types'

export type AuthContextValue = {
  user: User | null
  tokens: AuthTokens | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshTokens: () => Promise<void>
  reloadUser: () => Promise<void>
  clearSession: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
