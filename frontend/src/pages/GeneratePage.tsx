import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import type { QuizType } from '../api/types'
import { Alert, Button, Card, Field, Input } from '../components/ui'

const TOPIC_EXAMPLES = ['Photosynthesis', 'World War II', 'Python decorators', 'The French Revolution']

export function GeneratePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [topic, setTopic] = useState('')
  const [title, setTitle] = useState('')
  const [quizType, setQuizType] = useState<QuizType | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (selectedType: QuizType) =>
      quizzesApi.generate({
        topic: topic.trim(),
        title: title.trim() || `Quiz about ${topic.trim()}`,
        quiz_type: selectedType,
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

    if (!quizType) {
      setError('Please choose General or Niche.')
      return
    }

    mutation.mutate(quizType)
  }

  return (
    <div className="mx-auto w-full max-w-xl animate-fade-up">
      <h1 className="text-2xl font-bold text-white">Generate a quiz</h1>
      <p className="mt-1.5 text-sm text-zinc-400">
        Choose a quiz style and topic. We will write eight multiple-choice questions with explanations.
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

          <fieldset>
            <legend className="mb-1.5 block text-sm font-medium text-zinc-300">Quiz type</legend>
            <div className="grid gap-3 sm:grid-cols-2">
              <label
                className={`cursor-pointer rounded-xl border p-4 transition ${
                  quizType === 'general'
                    ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/30'
                    : 'border-zinc-800 bg-zinc-950/50 hover:border-zinc-700'
                }`}
              >
                <span className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
                  <input
                    type="radio"
                    name="quiz-type"
                    value="general"
                    checked={quizType === 'general'}
                    onChange={() => setQuizType('general')}
                    className="accent-indigo-500"
                  />
                  General
                </span>
                <span className="mt-2 block text-xs leading-relaxed text-zinc-400">
                  Broad, accessible questions about important ideas and facts.
                </span>
              </label>
              <label
                className={`cursor-pointer rounded-xl border p-4 transition ${
                  quizType === 'niche'
                    ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/30'
                    : 'border-zinc-800 bg-zinc-950/50 hover:border-zinc-700'
                }`}
              >
                <span className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
                  <input
                    type="radio"
                    name="quiz-type"
                    value="niche"
                    checked={quizType === 'niche'}
                    onChange={() => setQuizType('niche')}
                    className="accent-indigo-500"
                  />
                  Niche
                </span>
                <span className="mt-2 block text-xs leading-relaxed text-zinc-400">
                  Difficult questions about specialized details and advanced concepts.
                </span>
              </label>
            </div>
          </fieldset>

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
