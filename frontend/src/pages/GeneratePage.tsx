import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { quizzesApi } from '../api/quizzes'
import type { OptionKey, QuestionCreate, QuizType } from '../api/types'
import { Alert, Button, Card, Field, Input } from '../components/ui'

const TOPIC_EXAMPLES = ['Photosynthesis', 'World War II', 'Python decorators', 'The French Revolution']
const MAX_QUESTIONS = 50

type CreationMode = 'topic' | 'source' | 'manual'

function newQuestion(): QuestionCreate {
  return {
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_option: 'A',
    explanation: '',
  }
}

export function GeneratePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<CreationMode>('topic')
  const [topic, setTopic] = useState('')
  const [title, setTitle] = useState('')
  const [sourceText, setSourceText] = useState('')
  const [quizType, setQuizType] = useState<QuizType | null>(null)
  const [questions, setQuestions] = useState<QuestionCreate[]>([newQuestion()])
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => {
      const quizTitle = title.trim() || `Quiz about ${topic.trim()}`
      if (mode === 'manual') {
        return quizzesApi.create({
          title: quizTitle,
          topic: topic.trim(),
          quiz_type: quizType!,
          questions: questions.map((question) => ({
            ...question,
            question_text: question.question_text.trim(),
            option_a: question.option_a.trim(),
            option_b: question.option_b.trim(),
            option_c: question.option_c.trim(),
            option_d: question.option_d.trim(),
            explanation: question.explanation.trim(),
          })),
        })
      }

      return quizzesApi.generate({
        topic: topic.trim(),
        title: quizTitle,
        quiz_type: quizType!,
        ...(mode === 'source' ? { source_text: sourceText.trim() } : {}),
      })
    },
    onSuccess: (quiz) => {
      queryClient.invalidateQueries({ queryKey: ['quizzes'] })
      queryClient.setQueryData(['quiz', quiz.id], quiz)
      navigate(`/quiz/${quiz.id}`)
    },
    onError: (err: unknown) => {
      setError(err instanceof Error ? err.message : 'Could not create the quiz. Please try again.')
    },
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (!topic.trim()) {
      setError('Please enter a topic or subject.')
      return
    }

    if (!quizType) {
      setError('Please choose General or Niche.')
      return
    }

    if (mode === 'source' && !sourceText.trim()) {
      setError('Paste some source material to generate questions from.')
      return
    }

    if (
      mode === 'manual' &&
      questions.some((question) =>
        [
          question.question_text,
          question.option_a,
          question.option_b,
          question.option_c,
          question.option_d,
        ].some((value) => !value.trim()),
      )
    ) {
      setError('Complete each question and all four answer options.')
      return
    }

    mutation.mutate()
  }

  function updateQuestion(index: number, values: Partial<QuestionCreate>) {
    setQuestions((current) =>
      current.map((question, questionIndex) =>
        questionIndex === index ? { ...question, ...values } : question,
      ),
    )
  }

  return (
    <div className="mx-auto w-full max-w-3xl animate-fade-up">
      <h1 className="text-2xl font-bold text-white">Create a quiz</h1>
      <p className="mt-1.5 text-sm text-zinc-400">
        Generate questions with AI or write your own quiz from scratch.
      </p>

      <div className="mt-6 grid gap-2 sm:grid-cols-3" role="tablist" aria-label="Quiz creation method">
        {([
          ['topic', 'Generate from a topic'],
          ['source', 'Generate from my text'],
          ['manual', 'Write it myself'],
        ] as const).map(([value, label]) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={mode === value}
            onClick={() => {
              setMode(value)
              setError(null)
            }}
            className={`rounded-xl border px-3 py-3 text-sm font-semibold transition ${
              mode === value
                ? 'border-indigo-500 bg-indigo-500/10 text-white'
                : 'border-zinc-800 bg-zinc-900/50 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <Card className="mt-4 p-6">
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {error && <Alert>{error}</Alert>}

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Topic or subject" htmlFor="topic" hint="Used to organize your quiz.">
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

            <Field label="Quiz title" htmlFor="title" hint="Optional — we will name it for you.">
              <Input
                id="title"
                name="title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder={`Quiz about ${topic.trim() || 'your topic'}`}
              />
            </Field>
          </div>

          {mode === 'source' && (
            <Field
              label="Source material"
              htmlFor="source-text"
              hint="Questions and answers will be based only on this text. Maximum 20,000 characters."
            >
              <textarea
                id="source-text"
                required
                maxLength={20000}
                rows={9}
                value={sourceText}
                onChange={(event) => setSourceText(event.target.value)}
                placeholder="Paste your notes, study guide, or other material here…"
                className="w-full rounded-xl border border-zinc-800 bg-zinc-950/70 px-3.5 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              />
              <p className="mt-1.5 text-right text-xs text-zinc-500">
                {sourceText.length.toLocaleString()} / 20,000
              </p>
            </Field>
          )}

          {mode === 'manual' && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-end justify-between gap-2">
                <div>
                  <h2 className="text-sm font-semibold text-zinc-200">Your questions</h2>
                  <p className="mt-1 text-xs text-zinc-500">
                    Add 1 to {MAX_QUESTIONS} questions. Choose the correct option for each one.
                  </p>
                </div>
                <span className="text-xs text-zinc-500">
                  {questions.length} / {MAX_QUESTIONS}
                </span>
              </div>

              {questions.map((question, index) => (
                <section key={index} className="space-y-4 rounded-xl border border-zinc-800 p-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white">Question {index + 1}</h3>
                    {questions.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        className="px-2 py-1 text-xs text-rose-300"
                        onClick={() =>
                          setQuestions((current) => current.filter((_, i) => i !== index))
                        }
                      >
                        Remove
                      </Button>
                    )}
                  </div>

                  <Field label="Question" htmlFor={`question-${index}`}>
                    <textarea
                      id={`question-${index}`}
                      required
                      maxLength={2000}
                      rows={2}
                      value={question.question_text}
                      onChange={(event) =>
                        updateQuestion(index, { question_text: event.target.value })
                      }
                      className="w-full rounded-xl border border-zinc-800 bg-zinc-950/70 px-3.5 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                      placeholder="Write a question"
                    />
                  </Field>

                  <fieldset>
                    <legend className="mb-2 text-sm font-medium text-zinc-300">
                      Answer options — select the correct answer
                    </legend>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {(['A', 'B', 'C', 'D'] as const).map((option) => {
                        const field = `option_${option.toLowerCase()}` as
                          | 'option_a'
                          | 'option_b'
                          | 'option_c'
                          | 'option_d'
                        return (
                          <label
                            key={option}
                            className={`flex items-center gap-2 rounded-xl border px-3 py-2 ${
                              question.correct_option === option
                                ? 'border-emerald-500/50 bg-emerald-500/5'
                                : 'border-zinc-800 bg-zinc-950/40'
                            }`}
                          >
                            <input
                              type="radio"
                              name={`correct-option-${index}`}
                              value={option}
                              checked={question.correct_option === option}
                              onChange={() =>
                                updateQuestion(index, { correct_option: option as OptionKey })
                              }
                              className="accent-emerald-500"
                              aria-label={`Option ${option} is correct`}
                            />
                            <span className="text-xs font-semibold text-zinc-400">{option}</span>
                            <input
                              required
                              maxLength={500}
                              value={question[field]}
                              onChange={(event) => updateQuestion(index, { [field]: event.target.value })}
                              className="min-w-0 flex-1 bg-transparent text-sm text-zinc-100 outline-none placeholder:text-zinc-600"
                              placeholder={`Answer ${option}`}
                              aria-label={`Answer option ${option} for question ${index + 1}`}
                            />
                          </label>
                        )
                      })}
                    </div>
                  </fieldset>

                  <Field label="Explanation (optional)" htmlFor={`explanation-${index}`}>
                    <textarea
                      id={`explanation-${index}`}
                      maxLength={2000}
                      rows={2}
                      value={question.explanation}
                      onChange={(event) => updateQuestion(index, { explanation: event.target.value })}
                      className="w-full rounded-xl border border-zinc-800 bg-zinc-950/70 px-3.5 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                      placeholder="Explain why this is the correct answer"
                    />
                  </Field>
                </section>
              ))}

              <Button
                type="button"
                variant="secondary"
                className="w-full"
                disabled={questions.length >= MAX_QUESTIONS}
                onClick={() => setQuestions((current) => [...current, newQuestion()])}
              >
                + Add question
              </Button>
            </div>
          )}

          <fieldset>
            <legend className="mb-1.5 block text-sm font-medium text-zinc-300">Quiz type</legend>
            <div className="grid gap-3 sm:grid-cols-2">
              {([
                ['general', 'General', 'Broad, accessible questions about important ideas and facts.'],
                ['niche', 'Niche', 'Difficult questions about specialized details and advanced concepts.'],
              ] as const).map(([value, label, description]) => (
                <label
                  key={value}
                  className={`cursor-pointer rounded-xl border p-4 transition ${
                    quizType === value
                      ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/30'
                      : 'border-zinc-800 bg-zinc-950/50 hover:border-zinc-700'
                  }`}
                >
                  <span className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
                    <input
                      type="radio"
                      name="quiz-type"
                      value={value}
                      checked={quizType === value}
                      onChange={() => setQuizType(value)}
                      className="accent-indigo-500"
                    />
                    {label}
                  </span>
                  <span className="mt-2 block text-xs leading-relaxed text-zinc-400">
                    {description}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          <Button type="submit" loading={mutation.isPending} className="w-full">
            {mutation.isPending
              ? mode === 'manual'
                ? 'Saving quiz…'
                : 'Generating…'
              : mode === 'manual'
                ? 'Create quiz'
                : 'Generate quiz'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
