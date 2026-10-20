import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import { useAuth } from '../auth/useAuth'
import { Alert, Badge, Button, Card, EmptyState, Spinner } from '../components/ui'

export function DashboardPage() {
  const { user } = useAuth()
  const { data: quizzes, isPending, isError, error } = useQuery({
    queryKey: ['quizzes'],
    queryFn: quizzesApi.list,
  })

  return (
    <div className="animate-fade-up">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {user ? `Welcome back, ${user.username}` : 'My quizzes'}
          </h1>
          <p className="mt-1.5 text-sm text-zinc-400">
            {quizzes?.length
              ? `${quizzes.length} quiz${quizzes.length === 1 ? '' : 'zes'} in your library.`
              : 'Generate your first quiz to get started.'}
          </p>
        </div>
        <Link to="/generate">
          <Button>+ Generate quiz</Button>
        </Link>
      </div>

      <div className="mt-8">
        {isPending && (
          <div className="grid place-items-center rounded-2xl border border-zinc-800/80 bg-zinc-900/30 py-20">
            <Spinner className="size-6 text-indigo-400" />
          </div>
        )}

        {isError && (
          <Alert>
            {error instanceof Error ? error.message : 'Could not load your quizzes.'}
          </Alert>
        )}

        {!isPending && !isError && quizzes?.length === 0 && (
          <EmptyState
            title="No quizzes yet"
            description="Ask for any topic and QuizGen will build a five-question multiple-choice quiz for you."
            action={
              <Link to="/generate">
                <Button>Generate your first quiz</Button>
              </Link>
            }
          />
        )}

        {!isPending && !isError && quizzes && quizzes.length > 0 && (
          <ul className="grid gap-4 sm:grid-cols-2">
            {quizzes.map((quiz) => (
              <li key={quiz.id}>
                <Card className="flex h-full flex-col justify-between gap-4 p-5 transition hover:border-indigo-500/40">
                  <div>
                    <Badge tone="indigo">{quiz.topic}</Badge>
                    <h2 className="mt-3 text-base font-semibold text-white">{quiz.title}</h2>
                    <p className="mt-1 text-xs text-zinc-500">
                      {quiz.questions.length} question{quiz.questions.length === 1 ? '' : 's'}
                    </p>
                  </div>
                  <Link to={`/quiz/${quiz.id}`}>
                    <Button variant="secondary" className="w-full">
                      Take quiz
                    </Button>
                  </Link>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
