import { createContext } from 'react'
import type { User, UserCreate } from '../api/types'

export interface AuthContextValue {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  /** True while the initial "who am I" request is in flight. */
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (payload: UserCreate) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
