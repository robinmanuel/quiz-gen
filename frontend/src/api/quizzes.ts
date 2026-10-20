import { api } from './client'
import type { AnswerMap, Attempt, Quiz, QuizCreate } from './types'

export const quizzesApi = {
  generate: (payload: QuizCreate) => api.post<Quiz>('/quizzes/generate', payload),

  list: () => api.get<Quiz[]>('/quizzes/'),

  get: (quizId: number) => api.get<Quiz>(`/quizzes/${quizId}`),

  submit: (quizId: number, answers: AnswerMap) =>
    api.post<Attempt>(`/quizzes/${quizId}/submit`, { quiz_id: quizId, answers }),
}
