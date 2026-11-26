import type { InputHTMLAttributes } from 'react'

export const controlClass =
  'block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus-visible:border-blue-600 focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-blue-600 aria-invalid:border-red-600 disabled:bg-slate-100'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean
}

export function Input({ invalid, id, className = '', ...props }: InputProps) {
  return (
    <input
      id={id}
      aria-invalid={invalid || undefined}
      aria-describedby={invalid ? `${id}-error` : undefined}
      className={`${controlClass} ${className}`}
      {...props}
    />
  )
}
