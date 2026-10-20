import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import { Alert, Button, Card, Field, Input } from '../components/ui'

const TOPIC_EXAMPLES = ['Photosynthesis', 'World War II', 'Python decorators', 'The French Revolution']

export function GeneratePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [topic, setTopic] = useState('')
  const [title, setTitle] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      quizzesApi.generate({
        topic: topic.trim(),
        title: title.trim() || `Quiz about ${topic.trim()}`,
      }),
    onSuccess: (quiz) => {
      queryClient.invalidateQueries({ queryKey: ['quizzes'] })
      queryClient.setQueryData(['quiz', quiz.id], quiz)
      navigate(`/quiz/${quiz.id}`)
    },
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : 'Could not generate the quiz. Please try again.')
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (!topic.trim()) {
      setError('Please enter a topic.')
      return
    }

    mutation.mutate()
  }

  return (
    <div className="mx-auto w-full max-w-xl animate-fade-up">
      <h1 className="text-2xl font-bold text-white">Generate a quiz</h1>
      <p className="mt-1.5 text-sm text-zinc-400">
        Give us a topic and we will write five multiple-choice questions, each with an explanation.
      </p>

      <Card className="mt-8 p-6">
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {error && <Alert>{error}</Alert>}

          <Field label="Topic" htmlFor="topic" hint="Be as specific or as broad as you like.">
            <Input
              id="topic"
              name="topic"
              required
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              placeholder="e.g. The Renaissance"
              list="topic-examples"
            />
            <datalist id="topic-examples">
              {TOPIC_EXAMPLES.map((example) => (
                <option key={example} value={example} />
              ))}
            </datalist>
          </Field>

          <Field label="Title" htmlFor="title" hint="Optional — we will name it for you.">
            <Input
              id="title"
              name="title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder={`Quiz about ${topic.trim() || 'your topic'}`}
            />
          </Field>

          <Button type="submit" loading={mutation.isPending} className="w-full">
            {mutation.isPending ? 'Generating…' : 'Generate quiz'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
