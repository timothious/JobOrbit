import type { ButtonHTMLAttributes } from 'react'
import { Link, type LinkProps } from 'react-router'

type Variant = 'primary' | 'secondary'

const base =
  'inline-flex items-center justify-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'

const variants: Record<Variant, string> = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
}

type ButtonProps = { variant?: Variant } & (
  | ({ to?: undefined } & ButtonHTMLAttributes<HTMLButtonElement>)
  | ({ to: string } & Omit<LinkProps, 'to'>)
)

export function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  const classes = `${base} ${variants[variant]} ${className}`

  if (props.to !== undefined) {
    return <Link className={classes} {...props} />
  }
  return <button type="button" className={classes} {...props} />
}
