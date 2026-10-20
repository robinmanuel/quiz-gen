/**
 * Types mirroring the FastAPI schemas in backend/app/schemas.
 */

export interface User {
  id: number
  email: string
  username: string
}

export interface UserCreate {
  email: string
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export type OptionKey = 'A' | 'B' | 'C' | 'D'

export interface Question {
  id: number
  quiz_id: number
  question_text: string
  option_a: string
  option_b: string
  option_c: string
  option_d: string
  /** The API returns the correct answer with the question. It is never rendered
   *  before the attempt is submitted — see QuizPage. */
  correct_option: OptionKey
  explanation: string | null
}

export interface Quiz {
  id: number
  title: string
  topic: string
  owner_id: number
  questions: Question[]
}

export interface QuizCreate {
  title: string
  topic: string
}

export interface Attempt {
  id: number
  quiz_id: number
  user_id: number
  score: number
  total_questions: number
  correct_answers: number
  submitted_at: string
}

/** Answers are sent as { question_id: "A" } — the keys are strings in JSON. */
export type AnswerMap = Record<string, OptionKey>
