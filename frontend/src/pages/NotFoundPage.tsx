import { Link } from 'react-router-dom'
import { Button, Card } from '../components/ui'

export function NotFoundPage() {
  return (
    <div className="mx-auto mt-16 max-w-md text-center animate-fade-up">
      <Card className="p-10">
        <p className="text-5xl font-extrabold text-indigo-400">404</p>
        <h1 className="mt-4 text-xl font-bold text-white">Page not found</h1>
        <p className="mt-2 text-sm text-zinc-400">
          That page does not exist, or it may have been removed.
        </p>
        <Link to="/" className="mt-6 inline-block">
          <Button variant="secondary">Back to my quizzes</Button>
        </Link>
      </Card>
    </div>
  )
}
