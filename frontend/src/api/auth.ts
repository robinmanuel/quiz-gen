import { api } from './client'
import type { TokenResponse, User, UserCreate } from './types'

export const authApi = {
  /** OAuth2 password flow — the backend expects form-encoded credentials. */
  login: (username: string, password: string) =>
    api.postForm<TokenResponse>('/auth/token', { username, password }),

  register: (payload: UserCreate) => api.post<User>('/auth/register', payload),

  me: () => api.get<User>('/users/me'),
}
