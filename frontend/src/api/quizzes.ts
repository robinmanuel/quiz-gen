import { api } from './client'
import type {
  AnswerMap,
  Attempt,
  LeaderboardEntry,
  PublicQuiz,
  Quiz,
  QuizCreate,
  QuizManualCreate,
  QuizUpdate,
  SharedQuiz,
  UserAttempt,
} from './types'

export const quizzesApi = {
  generate: (payload: QuizCreate) => api.post<Quiz>('/quizzes/generate', payload),

  create: (payload: QuizManualCreate) => api.post<Quiz>('/quizzes/', payload),

  list: () => api.get<Quiz[]>('/quizzes/'),

  listAttempts: () => api.get<UserAttempt[]>('/quizzes/attempts'),

  listPublic: (search?: string) =>
    api.get<PublicQuiz[]>(
      search ? `/quizzes/public?search=${encodeURIComponent(search)}` : '/quizzes/public',
    ),

  getShared: (quizId: number) => api.get<SharedQuiz>(`/quizzes/shared/${quizId}`),

  leaderboard: () => api.get<LeaderboardEntry[]>('/quizzes/leaderboard'),

  quizLeaderboard: (quizId: number) =>
    api.get<LeaderboardEntry[]>(`/quizzes/${quizId}/leaderboard`),

  get: (quizId: number) => api.get<Quiz>(`/quizzes/${quizId}`),

  update: (quizId: number, payload: QuizUpdate) =>
    api.patch<Quiz>(`/quizzes/${quizId}`, payload),

  delete: (quizId: number) => api.delete(`/quizzes/${quizId}`),

  setPublic: (quizId: number, isPublic: boolean) =>
    api.patch<Quiz>(`/quizzes/${quizId}/share`, { is_public: isPublic }),

  submit: (quizId: number, answers: AnswerMap) =>
    api.post<Attempt>(`/quizzes/${quizId}/submit`, { quiz_id: quizId, answers }),
}
