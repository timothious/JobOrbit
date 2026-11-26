import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router'
import { ApiError, useAuthStatus, useLogin } from '@/api'
import { AuthLayout, Button, Field, Input } from '@/components'
import { safeNext } from '@/lib/safeNext'

export function LoginPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const status = useAuthStatus()
  const login = useLogin()
  const [password, setPassword] = useState('')
  const next = safeNext(params.get('next'))

  if (status.data && !status.data.setup_complete) return <Navigate to="/setup" replace />
  if (status.data?.authenticated) return <Navigate to={next} replace />

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    login.mutate({ password }, { onSuccess: () => navigate(next, { replace: true }) })
  }

  const error = login.error instanceof ApiError ? login.error.message : login.error && 'Sign-in failed.'

  return (
    <AuthLayout title="Sign in" description="Enter your JobOrbit password.">
      <form onSubmit={onSubmit} className="space-y-4">
        <Field label="Password" htmlFor="password" error={error || undefined}>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            autoFocus
            invalid={Boolean(error)}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Field>
        <Button type="submit" className="w-full" disabled={login.isPending}>
          {login.isPending ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
    </AuthLayout>
  )
}
