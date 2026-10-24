import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import { Alert, Badge, Button, Card, EmptyState, Spinner } from '../components/ui'

function LoadingPanel() {
  return (
    <div className="grid place-items-center rounded-2xl border border-zinc-800/80 bg-zinc-900/30 py-12">
      <Spinner className="size-6 text-indigo-400" />
    </div>
  )
}

export function CommunityPage() {
  const publicQuizzes = useQuery({
    queryKey: ['public-quizzes'],
    queryFn: quizzesApi.listPublic,
  })
  const leaderboard = useQuery({
    queryKey: ['leaderboard'],
    queryFn: quizzesApi.leaderboard,
  })

  return (
    <div className="animate-fade-up space-y-10">
      <header>
        <h1 className="text-2xl font-bold text-white">QuizGen community</h1>
        <p className="mt-1.5 text-sm text-zinc-400">
          Explore quizzes shared by the community and see the top scores.
        </p>
      </header>

      <section aria-labelledby="public-quizzes-heading">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 id="public-quizzes-heading" className="text-xl font-semibold text-white">
              Public quizzes
            </h2>
            <p className="mt-1 text-sm text-zinc-500">Quizzes their creators chose to share.</p>
          </div>
        </div>

        {publicQuizzes.isPending && <LoadingPanel />}
        {publicQuizzes.isError && (
          <Alert>
            {publicQuizzes.error instanceof Error
              ? publicQuizzes.error.message
              : 'Could not load public quizzes.'}
          </Alert>
        )}
        {!publicQuizzes.isPending && !publicQuizzes.isError && publicQuizzes.data.length === 0 && (
          <EmptyState
            title="No public quizzes yet"
            description="When someone shares a quiz, it will show up here."
          />
        )}
        {publicQuizzes.data && publicQuizzes.data.length > 0 && (
          <ul className="grid gap-4 sm:grid-cols-2">
            {publicQuizzes.data.map((quiz) => (
              <li key={quiz.id}>
                <Card className="flex h-full flex-col justify-between gap-4 p-5">
                  <div>
                    <div className="flex flex-wrap gap-2">
                      <Badge tone="indigo">{quiz.topic}</Badge>
                      <Badge tone={quiz.quiz_type === 'niche' ? 'rose' : 'emerald'}>
                        {quiz.quiz_type === 'niche' ? 'Niche' : 'General'}
                      </Badge>
                    </div>
                    <h3 className="mt-3 font-semibold text-white">{quiz.title}</h3>
                    <p className="mt-1 text-xs text-zinc-500">
                      By {quiz.owner_username} · {quiz.question_count} questions
                    </p>
                  </div>
                  <Link to={`/shared/${quiz.id}`}>
                    <Button variant="secondary" className="w-full">
                      Take quiz
                    </Button>
                  </Link>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="leaderboard-heading">
        <div className="mb-4">
          <h2 id="leaderboard-heading" className="text-xl font-semibold text-white">
            Leaderboard
          </h2>
          <p className="mt-1 text-sm text-zinc-500">
            Each player appears once, with their best score on a public quiz.
          </p>
        </div>

        {leaderboard.isPending && <LoadingPanel />}
        {leaderboard.isError && (
          <Alert>
            {leaderboard.error instanceof Error
              ? leaderboard.error.message
              : 'Could not load the leaderboard.'}
          </Alert>
        )}
        {!leaderboard.isPending && !leaderboard.isError && leaderboard.data.length === 0 && (
          <EmptyState
            title="No scores yet"
            description="Take a public quiz and your best result will appear here."
          />
        )}
        {leaderboard.data && leaderboard.data.length > 0 && (
          <Card className="overflow-x-auto">
            <table className="w-full min-w-[36rem] text-left text-sm">
              <thead className="border-b border-zinc-800 text-xs uppercase tracking-wide text-zinc-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Rank</th>
                  <th className="px-5 py-3 font-medium">Player</th>
                  <th className="px-5 py-3 font-medium">Best score</th>
                  <th className="px-5 py-3 font-medium">Quiz</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/70">
                {leaderboard.data.map((entry) => (
                  <tr key={`${entry.rank}-${entry.username}`} className="text-zinc-300">
                    <td className="px-5 py-4 font-semibold text-zinc-100">#{entry.rank}</td>
                    <td className="px-5 py-4">{entry.username}</td>
                    <td className="px-5 py-4 font-semibold text-emerald-300">
                      {entry.best_score}% ({entry.correct_answers}/{entry.total_questions})
                    </td>
                    <td className="px-5 py-4">
                      <span className="block text-zinc-200">{entry.quiz_title}</span>
                      <span className="text-xs text-zinc-500">{entry.quiz_topic}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>
    </div>
  )
}
