import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import type { AnswerMap, Attempt, OptionKey } from '../api/types'
import { cx } from '../lib/cx'
import { Alert, Badge, Button, Card, Spinner } from '../components/ui'

const OPTION_KEYS: OptionKey[] = ['A', 'B', 'C', 'D']

export function SharedQuizPage() {
  const { quizId: rawQuizId } = useParams()
  const quizId = Number(rawQuizId)
  const [answers, setAnswers] = useState<AnswerMap>({})
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [error, setError] = useState<string | null>(null)

  const quizQuery = useQuery({
    queryKey: ['shared-quiz', quizId],
    queryFn: () => quizzesApi.getShared(quizId),
    enabled: Number.isFinite(quizId),
  })
  const submitMutation = useMutation({
    mutationFn: () => quizzesApi.submit(quizId, answers),
    onSuccess: setAttempt,
    onError: (submitError: unknown) => {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Could not submit your answers. Please try again.',
      )
    },
  })

  if (!Number.isFinite(quizId)) {
    return <Alert>That quiz link is not valid.</Alert>
  }

  if (quizQuery.isPending) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner className="size-7 text-indigo-400" />
      </div>
    )
  }

  if (quizQuery.isError || !quizQuery.data) {
    return (
      <div className="space-y-4">
        <Alert>
          {quizQuery.error instanceof Error
            ? quizQuery.error.message
            : 'This shared quiz is unavailable.'}
        </Alert>
        <Link to="/community">
          <Button variant="secondary">Browse community quizzes</Button>
        </Link>
      </div>
    )
  }

  const quiz = quizQuery.data

  function retake() {
    setAnswers({})
    setAttempt(null)
    setError(null)
  }

  if (attempt) {
    const reviewByQuestion = new Map(
      (attempt.review ?? []).map((review) => [review.question_id, review]),
    )
    return (
      <div className="mx-auto w-full max-w-2xl animate-fade-up">
        <Card className="p-8 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-zinc-500">Your score</p>
          <p className="mt-2 text-6xl font-extrabold tabular-nums text-emerald-400">
            {attempt.score}%
          </p>
          <p className="mt-3 text-sm text-zinc-400">
            {attempt.correct_answers} of {attempt.total_questions} correct —{' '}
            <span className="text-zinc-200">{quiz.title}</span>
          </p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Button variant="secondary" onClick={retake}>Retake quiz</Button>
            <Link to="/community">
              <Button variant="ghost">Back to community</Button>
            </Link>
          </div>
        </Card>

        <h2 className="mt-10 text-lg font-semibold text-white">Review</h2>
        <ul className="mt-4 space-y-4">
          {quiz.questions.map((question, index) => {
            const review = reviewByQuestion.get(question.id)
            const correctOption = review?.correct_option
            const userAnswer = answers[String(question.id)]
            const options = [
              question.option_a,
              question.option_b,
              question.option_c,
              question.option_d,
            ]
            const isCorrect = userAnswer === correctOption

            return (
              <li key={question.id}>
                <Card className={cx('p-5', isCorrect ? 'border-emerald-500/30' : 'border-rose-500/30')}>
                  <p className="text-sm font-medium text-zinc-200">
                    {index + 1}. {question.question_text}
                  </p>
                  <p className="mt-3 text-sm text-zinc-400">
                    Your answer: {userAnswer ? `${userAnswer}. ${options[OPTION_KEYS.indexOf(userAnswer)]}` : 'Not answered'}
                  </p>
                  <p className="mt-1 text-sm text-emerald-300">
                    Correct answer: {correctOption}. {options[OPTION_KEYS.indexOf(correctOption ?? 'A')]}
                  </p>
                  {review?.explanation && (
                    <p className="mt-3 rounded-lg border border-zinc-800 bg-zinc-950/60 p-3 text-sm text-zinc-400">
                      {review.explanation}
                    </p>
                  )}
                </Card>
              </li>
            )
          })}
        </ul>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-2xl animate-fade-up">
      <header className="mb-6">
        <div className="flex flex-wrap gap-2">
          <Badge tone="indigo">{quiz.topic}</Badge>
          <Badge tone={quiz.quiz_type === 'niche' ? 'rose' : 'emerald'}>
            {quiz.quiz_type === 'niche' ? 'Niche' : 'General'}
          </Badge>
          <Badge>Shared by {quiz.owner_username}</Badge>
        </div>
        <h1 className="mt-3 text-2xl font-bold text-white">{quiz.title}</h1>
        <p className="mt-1 text-sm text-zinc-500">
          {quiz.questions.length} questions · Your best score on a shared quiz appears on the leaderboard.
        </p>
      </header>

      <div className="space-y-4">
        {quiz.questions.map((question, index) => {
          const options = [
            question.option_a,
            question.option_b,
            question.option_c,
            question.option_d,
          ]
          return (
            <Card key={question.id} className="p-5">
              <p className="font-semibold leading-relaxed text-zinc-100">
                {index + 1}. {question.question_text}
              </p>
              <div className="mt-4 space-y-2">
                {OPTION_KEYS.map((option, optionIndex) => {
                  const isSelected = answers[String(question.id)] === option
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() =>
                        setAnswers((previous) => ({
                          ...previous,
                          [String(question.id)]: option,
                        }))
                      }
                      className={cx(
                        'flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm transition',
                        isSelected
                          ? 'border-indigo-500 bg-indigo-500/15 text-white ring-2 ring-indigo-500/40'
                          : 'border-zinc-800 bg-zinc-950/50 text-zinc-300 hover:border-zinc-700',
                      )}
                    >
                      <span className="font-bold text-indigo-300">{option}.</span>
                      <span>{options[optionIndex]}</span>
                    </button>
                  )
                })}
              </div>
            </Card>
          )
        })}
      </div>

      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <div className="mt-6 flex items-center justify-between gap-4">
        <span className="text-xs text-zinc-500">
          {Object.keys(answers).length}/{quiz.questions.length} answered
        </span>
        <Button
          onClick={() => {
            setError(null)
            submitMutation.mutate()
          }}
          loading={submitMutation.isPending}
        >
          Submit answers
        </Button>
      </div>
    </div>
  )
}
