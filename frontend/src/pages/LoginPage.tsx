import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuth } from '../auth/useAuth'
import { Alert, Button, Card, Field, Input } from '../components/ui'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => login(username.trim(), password),
    onSuccess: () => {
      const from = (location.state as { from?: string } | null)?.from ?? '/'
      navigate(from, { replace: true })
    },
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : 'Unable to log in. Please try again.')
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate()
  }

  return (
    <div className="mx-auto mt-6 w-full max-w-md animate-fade-up">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold text-white">Welcome back</h1>
        <p className="mt-1.5 text-sm text-zinc-400">Log in to continue building your quiz library.</p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {error && <Alert>{error}</Alert>}

          <Field label="Username" htmlFor="username">
            <Input
              id="username"
              name="username"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="ada_lovelace"
            />
          </Field>

          <Field label="Password" htmlFor="password">
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </Field>

          <Button type="submit" loading={mutation.isPending} className="w-full">
            Log in
          </Button>
        </form>
      </Card>

      <p className="mt-5 text-center text-sm text-zinc-400">
        No account yet?{' '}
        <Link to="/register" className="font-semibold text-indigo-400 hover:text-indigo-300">
          Create one
        </Link>
      </p>
    </div>
  )
}
