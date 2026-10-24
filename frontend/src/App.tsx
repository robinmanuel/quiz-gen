import { Navigate, Route, Routes } from 'react-router-dom'
import { GuestRoute, ProtectedRoute } from './auth/ProtectedRoute'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { CommunityPage } from './pages/CommunityPage'
import { GeneratePage } from './pages/GeneratePage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { QuizPage } from './pages/QuizPage'
import { RegisterPage } from './pages/RegisterPage'
import { SharedQuizPage } from './pages/SharedQuizPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route element={<GuestRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/generate" element={<GeneratePage />} />
          <Route path="/quiz/:quizId" element={<QuizPage />} />
          <Route path="/shared/:quizId" element={<SharedQuizPage />} />
        </Route>

        <Route path="/404" element={<NotFoundPage />} />
        <Route path="/community" element={<CommunityPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  )
}
