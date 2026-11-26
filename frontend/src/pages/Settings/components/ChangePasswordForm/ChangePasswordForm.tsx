import { useState, type FormEvent } from 'react'
import { ApiError, useChangePassword } from '@/api'
import { Button, Card, Field, Input } from '@/components'
import { toast } from '@/lib/toast'

export function ChangePasswordForm() {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const change = useChangePassword()
  const error = (field: string) => (change.error instanceof ApiError ? change.error.fieldError(field) : undefined)

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    change.mutate(
      { current_password: current, new_password: next },
      {
        onSuccess: () => {
          setCurrent('')
          setNext('')
          toast.success('Password changed. Other devices were signed out.')
        },
      },
    )
  }

  return (
    <Card>
      <h2 className="text-base font-semibold">Change password</h2>
      <form onSubmit={onSubmit} className="mt-4 grid gap-4 md:grid-cols-2">
        <Field label="Current password" htmlFor="current-password" error={error('current_password')}>
          <Input
            id="current-password"
            type="password"
            autoComplete="current-password"
            required
            invalid={Boolean(error('current_password'))}
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
          />
        </Field>
        <Field
          label="New password"
          htmlFor="new-password"
          hint="At least 12 characters."
          error={error('new_password')}
        >
          <Input
            id="new-password"
            type="password"
            autoComplete="new-password"
            minLength={12}
            maxLength={128}
            required
            invalid={Boolean(error('new_password'))}
            value={next}
            onChange={(e) => setNext(e.target.value)}
          />
        </Field>
        <div className="md:col-span-2">
          <Button type="submit" variant="secondary" disabled={change.isPending}>
            {change.isPending ? 'Changing…' : 'Change password'}
          </Button>
        </div>
      </form>
    </Card>
  )
}
