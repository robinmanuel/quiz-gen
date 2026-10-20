import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  LabelHTMLAttributes,
  ReactNode,
  Ref,
} from 'react'
import { cx } from '../lib/cx'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const buttonVariants: Record<ButtonVariant, string> = {
  primary:
    'bg-gradient-to-r from-indigo-500 to-violet-500 text-white shadow-lg shadow-indigo-500/20 hover:from-indigo-400 hover:to-violet-400 focus-visible:outline-indigo-400',
  secondary:
    'border border-zinc-700 bg-zinc-900/60 text-zinc-100 hover:border-zinc-600 hover:bg-zinc-800/60 focus-visible:outline-zinc-400',
  ghost: 'text-zinc-300 hover:bg-zinc-800/60 hover:text-white focus-visible:outline-zinc-400',
  danger: 'border border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 focus-visible:outline-rose-400',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  loading?: boolean
  ref?: Ref<HTMLButtonElement>
}

export function Button({
  className,
  variant = 'primary',
  loading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cx(
        'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold',
        'transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-50',
        buttonVariants[variant],
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="size-4" />}
      {children}
    </button>
  )
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean
  ref?: Ref<HTMLInputElement>
}

export function Input({ className, invalid = false, ...props }: InputProps) {
  return (
    <input
      className={cx(
        'w-full rounded-xl border bg-zinc-950/70 px-3.5 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500',
        'transition focus:outline-none focus:ring-2',
        invalid
          ? 'border-rose-500/60 focus:border-rose-500 focus:ring-rose-500/30'
          : 'border-zinc-800 focus:border-indigo-500 focus:ring-indigo-500/30',
        className,
      )}
      {...props}
    />
  )
}

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  children: ReactNode
}

export function Label({ className, children, ...props }: LabelProps) {
  return (
    <label className={cx('mb-1.5 block text-sm font-medium text-zinc-300', className)} {...props}>
      {children}
    </label>
  )
}

interface FieldProps {
  label: string
  htmlFor: string
  error?: string
  hint?: string
  children: ReactNode
}

export function Field({ label, htmlFor, error, hint, children }: FieldProps) {
  return (
    <div>
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {error ? (
        <p className="mt-1.5 text-xs text-rose-400">{error}</p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-zinc-500">{hint}</p>
      ) : null}
    </div>
  )
}

export function Spinner({ className }: { className?: string }) {
  return (
    <svg
      className={cx('animate-spin', className ?? 'size-5')}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-90"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  )
}

export function Alert({
  tone = 'error',
  children,
}: {
  tone?: 'error' | 'success' | 'info'
  children: ReactNode
}) {
  const tones = {
    error: 'border-rose-500/30 bg-rose-500/10 text-rose-200',
    success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
    info: 'border-sky-500/30 bg-sky-500/10 text-sky-200',
  }
  return (
    <div
      role="alert"
      className={cx('rounded-xl border px-4 py-3 text-sm whitespace-pre-line', tones[tone])}
    >
      {children}
    </div>
  )
}

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div
      className={cx(
        'rounded-2xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-sm shadow-xl shadow-black/20',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function Badge({
  tone = 'neutral',
  children,
}: {
  tone?: 'neutral' | 'indigo' | 'emerald' | 'rose'
  children: ReactNode
}) {
  const tones = {
    neutral: 'border-zinc-700 bg-zinc-800/70 text-zinc-300',
    indigo: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-300',
    emerald: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
    rose: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
  }
  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium',
        tones[tone],
      )}
    >
      {children}
    </span>
  )
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cx('inline-flex items-center gap-2 font-extrabold tracking-tight', className)}>
      <span className="grid size-8 place-items-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 text-sm text-white shadow-lg shadow-indigo-500/30">
        ?
      </span>
      <span className="text-lg text-white">
        Quiz<span className="text-indigo-400">Gen</span>
      </span>
    </span>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/30 px-6 py-14 text-center">
      <p className="text-base font-semibold text-zinc-200">{title}</p>
      <p className="mt-1.5 max-w-md text-sm text-zinc-500">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
