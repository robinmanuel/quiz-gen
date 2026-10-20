const TOKEN_KEY = 'quizgen.token'
const USER_KEY = 'quizgen.user'

/**
 * The API client reads the token straight from localStorage so that requests
 * always carry the latest value without depending on React render order.
 */
export const tokenStorage = {
  get: (): string | null => localStorage.getItem(TOKEN_KEY),
  set: (token: string): void => localStorage.setItem(TOKEN_KEY, token),
  clear: (): void => localStorage.removeItem(TOKEN_KEY),
}

export const userStorage = {
  get: (): string | null => localStorage.getItem(USER_KEY),
  set: (user: unknown): void => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  clear: (): void => localStorage.removeItem(USER_KEY),
}
