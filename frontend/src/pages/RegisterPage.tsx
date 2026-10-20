import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuth } from '../auth/useAuth'
import { Alert, Button, Card, Field, Input } from '../components/ui'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      register({ email: email.trim(), username: username.trim(), password }),
    onSuccess: () => navigate('/', { replace: true }),
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : 'Unable to create the account. Please try again.')
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (password !== confirmPassword) {
      setError('The two passwords do not match.')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.')
      return
    }

    mutation.mutate()
  }

  return (
    <div className="mx-auto mt-6 w-full max-w-md animate-fade-up">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold text-white">Create your account</h1>
        <p className="mt-1.5 text-sm text-zinc-400">Generate AI quizzes and track your scores.</p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {error && <Alert>{error}</Alert>}

          <Field label="Email" htmlFor="email">
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="ada@example.com"
            />
          </Field>

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

          <Field label="Password" htmlFor="password" hint="At least 6 characters.">
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </Field>

          <Field label="Confirm password" htmlFor="confirm-password">
            <Input
              id="confirm-password"
              name="confirm-password"
              type="password"
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="••••••••"
            />
          </Field>

          <Button type="submit" loading={mutation.isPending} className="w-full">
            Create account
          </Button>
        </form>
      </Card>

      <p className="mt-5 text-center text-sm text-zinc-400">
        Already registered?{' '}
        <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300">
          Log in
        </Link>
      </p>
    </div>
  )
}
