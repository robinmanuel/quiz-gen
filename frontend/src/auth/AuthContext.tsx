import { useCallback, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { ApiError } from '../api/client'
import type { User, UserCreate } from '../api/types'
import { tokenStorage, userStorage } from '../lib/storage'
import { AuthContext } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => tokenStorage.get())
  const queryClient = useQueryClient()

  const meQuery = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      try {
        return await authApi.me()
      } catch (error) {
        // An expired or tampered token drops the session instead of leaving
        // the UI in a half-authenticated state.
        if (error instanceof ApiError && error.status === 401) {
          tokenStorage.clear()
          userStorage.clear()
          setToken(null)
        }
        throw error
      }
    },
    enabled: token !== null,
    retry: false,
    staleTime: 5 * 60_000,
  })

  const login = useCallback(
    async (username: string, password: string) => {
      const { access_token } = await authApi.login(username, password)
      tokenStorage.set(access_token)
      setToken(access_token)
      queryClient.removeQueries({ queryKey: ['me'] })
    },
    [queryClient],
  )

  const register = useCallback(
    async (payload: UserCreate) => {
      await authApi.register(payload)
      await login(payload.username, payload.password)
    },
    [login],
  )

  const logout = useCallback(() => {
    tokenStorage.clear()
    userStorage.clear()
    setToken(null)
    queryClient.clear()
  }, [queryClient])

  const value = useMemo(
    () => ({
      user: (meQuery.data ?? null) as User | null,
      token,
      isAuthenticated: token !== null && meQuery.data != null,
      isLoading: token !== null && meQuery.isPending,
      login,
      register,
      logout,
    }),
    [meQuery.data, meQuery.isPending, token, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
