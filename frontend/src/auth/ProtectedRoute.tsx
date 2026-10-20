import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth'
import { Spinner } from '../components/ui'

function FullScreenLoader() {
  return (
    <div className="grid min-h-[60vh] place-items-center">
      <Spinner className="size-7 text-indigo-400" />
    </div>
  )
}

/** Requires a valid session; redirects to the login page otherwise. */
export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <FullScreenLoader />
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

/** Keeps signed-in users away from the login/register screens. */
export function GuestRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <FullScreenLoader />
  if (isAuthenticated) return <Navigate to="/" replace />
  return <Outlet />
}
