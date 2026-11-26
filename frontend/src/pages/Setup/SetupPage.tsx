import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'
import { ApiError, useAuthStatus, useCountryOptions, useSetup } from '@/api'
import { AuthLayout, Button, CountryMultiSelect, CountrySelect, Field, Input } from '@/components'
import { exampleProfile } from '@/config/exampleProfile'

const MIN_PASSWORD = 12
const FORM_FIELDS = ['password', 'profile.citizenship_country_codes', 'profile.residence_country_code', 'timezone']

export function SetupPage() {
  const navigate = useNavigate()
  const status = useAuthStatus()
  const countries = useCountryOptions()
  const setup = useSetup()

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [fullName, setFullName] = useState('')
  const [citizenships, setCitizenships] = useState(exampleProfile.citizenshipCountryCodes)
  const [residence, setResidence] = useState<string | null>(exampleProfile.residenceCountryCode)
  const [timezone, setTimezone] = useState(() => Intl.DateTimeFormat().resolvedOptions().timeZone)
  const [mismatch, setMismatch] = useState(false)

  if (status.data?.setup_complete) return <Navigate to="/login" replace />

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    setMismatch(password !== confirm)
    if (password !== confirm) return
    setup.mutate(
      {
        password,
        timezone,
        profile: {
          full_name: fullName.trim() || null,
          citizenship_country_codes: citizenships,
          residence_country_code: residence,
        },
      },
      { onSuccess: () => navigate('/', { replace: true }) },
    )
  }

  const apiError = setup.error instanceof ApiError ? setup.error : null
  const fieldError = (field: string) => apiError?.fieldError(field)
  const options = countries.data ?? []
  // Errors the form cannot attach to a field (e.g. an unknown country) are shown at the bottom.
  const otherErrors = apiError
    ? apiError.details.length
      ? apiError.details
          .filter((d) => !FORM_FIELDS.some((f) => d.field === f || d.field.startsWith(`${f}.`)))
          .map((d) => d.message)
      : [apiError.message]
    : []

  return (
    <AuthLayout
      title="Set up JobOrbit"
      description="Choose a password and the basics of your profile. You can change everything later."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Field
          label="Password"
          htmlFor="password"
          hint={`At least ${MIN_PASSWORD} characters.`}
          error={fieldError('password')}
        >
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            minLength={MIN_PASSWORD}
            maxLength={128}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Field>
        <Field label="Confirm password" htmlFor="confirm" error={mismatch ? 'Passwords do not match.' : undefined}>
          <Input
            id="confirm"
            type="password"
            autoComplete="new-password"
            required
            invalid={mismatch}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </Field>
        <Field label="Full name" htmlFor="full-name" hint="Optional.">
          <Input id="full-name" maxLength={120} value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </Field>
        <Field label="Citizenship" htmlFor="citizenship" error={fieldError('profile.citizenship_country_codes')}>
          <CountryMultiSelect id="citizenship" options={options} value={citizenships} onChange={setCitizenships} />
        </Field>
        <Field label="Country of residence" htmlFor="residence" error={fieldError('profile.residence_country_code')}>
          <CountrySelect id="residence" options={options} value={residence} onChange={setResidence} />
        </Field>
        <Field label="Timezone" htmlFor="timezone" hint="Detected from your browser." error={fieldError('timezone')}>
          <Input id="timezone" required value={timezone} onChange={(e) => setTimezone(e.target.value)} />
        </Field>
        {otherErrors.map((message) => (
          <p key={message} role="alert" className="text-sm text-red-600">
            {message}
          </p>
        ))}
        <Button type="submit" className="w-full" disabled={setup.isPending}>
          {setup.isPending ? 'Setting up…' : 'Finish setup'}
        </Button>
      </form>
    </AuthLayout>
  )
}
