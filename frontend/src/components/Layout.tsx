import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { cx } from '../lib/cx'
import { Button, Logo } from './ui'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  cx(
    'rounded-lg px-3 py-2 text-sm font-medium transition',
    isActive ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-100',
  )

export function Layout() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-20 border-b border-zinc-800/70 bg-zinc-950/70 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-5xl items-center justify-between gap-4 px-4">
          <NavLink to="/" className="shrink-0">
            <Logo />
          </NavLink>

          {isAuthenticated ? (
            <div className="flex items-center gap-1 sm:gap-2">
              <NavLink to="/" end className={navLinkClass}>
                My quizzes
              </NavLink>
              <NavLink to="/generate" className={navLinkClass}>
                Create quiz
              </NavLink>
              <NavLink to="/community" className={navLinkClass}>
                Community
              </NavLink>
              <span className="ml-2 hidden max-w-[12rem] truncate text-sm text-zinc-400 sm:block">
                {user?.username}
              </span>
              <Button variant="ghost" onClick={handleLogout} className="px-3">
                Log out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <NavLink to="/community" className={navLinkClass}>
                Community
              </NavLink>
              <NavLink to="/login" className={navLinkClass}>
                Log in
              </NavLink>
              <NavLink to="/register" className={navLinkClass}>
                Sign up
              </NavLink>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-zinc-800/70 py-6">
        <p className="text-center text-xs text-zinc-600">
          QuizGen — AI-powered quizzes, generated with OpenAI.
        </p>
      </footer>
    </div>
  )
}
