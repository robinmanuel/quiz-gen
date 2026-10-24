import { tokenStorage } from '../lib/storage'

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/+$/, '')

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface FastApiValidationError {
  loc?: (string | number)[]
  msg?: string
}

function parseDetail(data: unknown, status: number): string {
  if (data && typeof data === 'object' && 'detail' in data) {
    const detail = (data as { detail: unknown }).detail

    if (typeof detail === 'string') return detail

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          const err = item as FastApiValidationError
          const field = err.loc?.filter((part) => part !== 'body').join('.')
          return field ? `${field}: ${err.msg ?? 'invalid'}` : (err.msg ?? 'invalid')
        })
        .join('\n')
      if (messages) return messages
    }
  }

  if (status === 0) return 'Cannot reach the API. Is the backend running?'
  return `Request failed with status ${status}`
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = tokenStorage.get()

  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, 'Cannot reach the API. Is the backend running?')
  }

  if (response.status === 204) return undefined as T

  const text = await response.text()
  let data: unknown = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, parseDetail(data, response.status))
  }

  return data as T
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  postForm: <T>(path: string, form: Record<string, string>) =>
    request<T>(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(form).toString(),
    }),
}
