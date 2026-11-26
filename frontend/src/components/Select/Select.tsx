import type { SelectHTMLAttributes } from 'react'
import { controlClass } from '@/components/Input'

export function Select({ className = '', ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`${controlClass} ${className}`} {...props} />
}
