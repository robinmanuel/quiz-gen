import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import type { AnswerMap, Attempt, OptionKey, Question } from '../api/types'
import { cx } from '../lib/cx'
import { Alert, Badge, Button, Card, Spinner } from '../components/ui'

function optionsOf(question: Question): Array<{ key: OptionKey; text: string }> {
  return [
    { key: 'A', text: question.option_a },
    { key: 'B', text: question.option_b },
    { key: 'C', text: question.option_c },
    { key: 'D', text: question.option_d },
  ]
}

export function QuizPage() {
  const { quizId: rawQuizId } = useParams()
  const quizId = Number(rawQuizId)

  const [answers, setAnswers] = useState<AnswerMap>({})
  const [index, setIndex] = useState(0)
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data: quiz, isPending, isError, error: loadError } = useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => quizzesApi.get(quizId),
    enabled: Number.isFinite(quizId),
  })

  const submitMutation = useMutation({
    mutationFn: () => quizzesApi.submit(quizId, answers),
    onSuccess: (result) => setAttempt(result),
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : 'Could not submit your answers. Please try again.')
    },
  })

  function selectAnswer(questionId: number, option: OptionKey) {
    setAnswers((previous) => ({ ...previous, [String(questionId)]: option }))
  }

  function retake() {
    setAnswers({})
    setIndex(0)
    setAttempt(null)
    setError(null)
  }

  if (!Number.isFinite(quizId)) {
    return <Alert>That quiz id is not valid.</Alert>
  }

  if (isPending) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner className="size-7 text-indigo-400" />
      </div>
    )
  }

  if (isError || !quiz) {
    return (
      <div className="space-y-4">
        <Alert>{loadError instanceof Error ? loadError.message : 'Could not load this quiz.'}</Alert>
        <Link to="/">
          <Button variant="secondary">Back to my quizzes</Button>
        </Link>
      </div>
    )
  }

  if (quiz.questions.length === 0) {
    return (
      <div className="space-y-4">
        <Alert>This quiz has no questions. Try generating a new one.</Alert>
        <Link to="/generate">
          <Button>Generate a new quiz</Button>
        </Link>
      </div>
    )
  }

  if (attempt) {
    return (
      <ResultsView quiz={quiz} answers={answers} attempt={attempt} onRetake={retake} />
    )
  }

  const question = quiz.questions[index]
  const total = quiz.questions.length
  const answeredCount = quiz.questions.filter((q) => answers[String(q.id)]).length
  const isLast = index === total - 1
  const selected = answers[String(question.id)]

  return (
    <div className="mx-auto w-full max-w-2xl animate-fade-up">
      <div className="mb-6">
        <Badge tone="indigo">{quiz.topic}</Badge>
        <h1 className="mt-3 text-2xl font-bold text-white">{quiz.title}</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Question {index + 1} of {total}
        </p>
      </div>

      <div className="mb-6 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-300"
          style={{ width: `${((index + 1) / total) * 100}%` }}
        />
      </div>

      <Card className="p-6">
        <p className="text-lg font-semibold leading-relaxed text-zinc-100">
          {question.question_text}
        </p>

        <div className="mt-5 space-y-2.5">
          {optionsOf(question).map((option) => {
            const isSelected = selected === option.key
            return (
              <button
                key={option.key}
                type="button"
                onClick={() => selectAnswer(question.id, option.key)}
                className={cx(
                  'flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm transition',
                  isSelected
                    ? 'border-indigo-500 bg-indigo-500/15 text-white ring-2 ring-indigo-500/40'
                    : 'border-zinc-800 bg-zinc-950/50 text-zinc-300 hover:border-zinc-700 hover:bg-zinc-900/60',
                )}
              >
                <span
                  className={cx(
                    'grid size-7 shrink-0 place-items-center rounded-lg text-xs font-bold',
                    isSelected
                      ? 'bg-indigo-500 text-white'
                      : 'border border-zinc-700 bg-zinc-900 text-zinc-400',
                  )}
                >
                  {option.key}
                </span>
                <span className="leading-snug">{option.text}</span>
              </button>
            )
          })}
        </div>
      </Card>

      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <div className="mt-6 flex items-center justify-between gap-3">
        <Button
          variant="secondary"
          onClick={() => setIndex((current) => Math.max(0, current - 1))}
          disabled={index === 0}
        >
          Back
        </Button>

        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-500">
            {answeredCount}/{total} answered
          </span>
          {isLast ? (
            <Button
              onClick={() => {
                setError(null)
                submitMutation.mutate()
              }}
              loading={submitMutation.isPending}
            >
              Submit answers
            </Button>
          ) : (
            <Button onClick={() => setIndex((current) => Math.min(total - 1, current + 1))}>
              Next
            </Button>
          )}
        </div>
      </div>

      {isLast && answeredCount < total && (
        <p className="mt-3 text-right text-xs text-amber-400/80">
          {total - answeredCount} unanswered question{total - answeredCount === 1 ? '' : 's'} will be
          marked incorrect.
        </p>
      )}
    </div>
  )
}

function ResultsView({
  quiz,
  answers,
  attempt,
  onRetake,
}: {
  quiz: { title: string; topic: string; questions: Question[] }
  answers: AnswerMap
  attempt: Attempt
  onRetake: () => void
}) {
  const score = attempt.score

  return (
    <div className="mx-auto w-full max-w-2xl animate-fade-up">
      <Card className="p-8 text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-zinc-500">Your score</p>
        <p
          className={cx(
            'mt-2 text-6xl font-extrabold tabular-nums',
            score >= 80 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-rose-400',
          )}
        >
          {score}%
        </p>
        <p className="mt-3 text-sm text-zinc-400">
          {attempt.correct_answers} of {attempt.total_questions} correct —{' '}
          <span className="text-zinc-200">{quiz.title}</span>
        </p>

        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Button variant="secondary" onClick={onRetake}>
            Retake quiz
          </Button>
          <Link to="/">
            <Button variant="ghost">Back to my quizzes</Button>
          </Link>
        </div>
      </Card>

      <h2 className="mt-10 text-lg font-semibold text-white">Review</h2>
      <ul className="mt-4 space-y-4">
        {quiz.questions.map((question, position) => {
          const userAnswer = answers[String(question.id)]
          const isCorrect = userAnswer === question.correct_option

          return (
            <li key={question.id}>
              <Card className={cx('p-5', isCorrect ? 'border-emerald-500/30' : 'border-rose-500/30')}>
                <div className="flex items-start gap-3">
                  <span
                    className={cx(
                      'mt-0.5 grid size-6 shrink-0 place-items-center rounded-full text-xs font-bold',
                      isCorrect
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-rose-500/20 text-rose-300',
                    )}
                  >
                    {isCorrect ? '✓' : '✕'}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-zinc-200">
                      {position + 1}. {question.question_text}
                    </p>

                    <dl className="mt-3 space-y-1.5 text-sm">
                      <div className="flex flex-wrap gap-x-2">
                        <dt className="text-zinc-500">Your answer:</dt>
                        <dd className={userAnswer ? 'text-zinc-200' : 'text-amber-300'}>
                          {userAnswer ? `${userAnswer}. ${optionsOf(question).find((o) => o.key === userAnswer)?.text}` : 'Not answered'}
                        </dd>
                      </div>
                      {!isCorrect && (
                        <div className="flex flex-wrap gap-x-2">
                          <dt className="text-zinc-500">Correct answer:</dt>
                          <dd className="text-emerald-300">
                            {question.correct_option}.{' '}
                            {optionsOf(question).find((o) => o.key === question.correct_option)?.text}
                          </dd>
                        </div>
                      )}
                    </dl>

                    {question.explanation && (
                      <p className="mt-3 rounded-lg border border-zinc-800 bg-zinc-950/60 p-3 text-sm text-zinc-400">
                        {question.explanation}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
