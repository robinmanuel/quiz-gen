import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import { useAuth } from '../auth/useAuth'
import { Alert, Badge, Button, Card, EmptyState, Spinner } from '../components/ui'

export function DashboardPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [shareError, setShareError] = useState<string | null>(null)
  const [copiedQuizId, setCopiedQuizId] = useState<number | null>(null)
  const { data: quizzes, isPending, isError, error } = useQuery({
    queryKey: ['quizzes'],
    queryFn: quizzesApi.list,
  })
  const sharingMutation = useMutation({
    mutationFn: ({ quizId, isPublic }: { quizId: number; isPublic: boolean }) =>
      quizzesApi.setPublic(quizId, isPublic),
    onSuccess: (updatedQuiz) => {
      queryClient.setQueryData(
        ['quizzes'],
        (current: typeof quizzes | undefined) =>
          current?.map((quiz) => (quiz.id === updatedQuiz.id ? updatedQuiz : quiz)),
      )
      queryClient.invalidateQueries({ queryKey: ['public-quizzes'] })
      setShareError(null)
    },
    onError: (err: unknown) => {
      setShareError(err instanceof Error ? err.message : 'Could not update quiz sharing.')
    },
  })

  async function copyShareLink(quizId: number) {
    const shareUrl = `${window.location.origin}/shared/${quizId}`
    try {
      await navigator.clipboard.writeText(shareUrl)
      setCopiedQuizId(quizId)
      setShareError(null)
    } catch {
      setShareError('Could not copy the link. You can copy it from the address bar instead.')
    }
  }

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

      {shareError && (
        <div className="mt-4">
          <Alert>{shareError}</Alert>
        </div>
      )}

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
            description="Choose General or Niche, then QuizGen will build an eight-question multiple-choice quiz."
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
                    <div className="flex flex-wrap gap-2">
                      <Badge tone="indigo">{quiz.topic}</Badge>
                      <Badge tone={quiz.quiz_type === 'niche' ? 'rose' : 'emerald'}>
                        {quiz.quiz_type === 'niche' ? 'Niche' : 'General'}
                      </Badge>
                    </div>
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
                  <div className="space-y-2 border-t border-zinc-800 pt-4">
                    <Button
                      variant={quiz.is_public ? 'danger' : 'secondary'}
                      className="w-full"
                      loading={sharingMutation.isPending}
                      onClick={() =>
                        sharingMutation.mutate({
                          quizId: quiz.id,
                          isPublic: !quiz.is_public,
                        })
                      }
                    >
                      {quiz.is_public ? 'Make private' : 'Share publicly'}
                    </Button>
                    {quiz.is_public && (
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/shared/${quiz.id}`}
                          className="min-w-0 flex-1 truncate text-xs text-indigo-300 underline"
                        >
                          {`${window.location.origin}/shared/${quiz.id}`}
                        </Link>
                        <Button
                          type="button"
                          variant="ghost"
                          className="shrink-0 px-2"
                          onClick={() => void copyShareLink(quiz.id)}
                        >
                          {copiedQuizId === quiz.id ? 'Copied' : 'Copy link'}
                        </Button>
                      </div>
                    )}
                  </div>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
