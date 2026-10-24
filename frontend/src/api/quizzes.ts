import { api } from './client'
import type {
  AnswerMap,
  Attempt,
  LeaderboardEntry,
  PublicQuiz,
  Quiz,
  QuizCreate,
  SharedQuiz,
} from './types'

export const quizzesApi = {
  generate: (payload: QuizCreate) => api.post<Quiz>('/quizzes/generate', payload),

  list: () => api.get<Quiz[]>('/quizzes/'),

  listPublic: () => api.get<PublicQuiz[]>('/quizzes/public'),

  getShared: (quizId: number) => api.get<SharedQuiz>(`/quizzes/shared/${quizId}`),

  leaderboard: () => api.get<LeaderboardEntry[]>('/quizzes/leaderboard'),

  get: (quizId: number) => api.get<Quiz>(`/quizzes/${quizId}`),

  setPublic: (quizId: number, isPublic: boolean) =>
    api.patch<Quiz>(`/quizzes/${quizId}/share`, { is_public: isPublic }),

  submit: (quizId: number, answers: AnswerMap) =>
    api.post<Attempt>(`/quizzes/${quizId}/submit`, { quiz_id: quizId, answers }),
}
