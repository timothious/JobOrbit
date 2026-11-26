import { useState, type FormEvent } from 'react'
import { ApiError, useCountryOptions, useUpdateProfile, type Profile } from '@/api'
import { Button, Card, CountryMultiSelect, CountrySelect, Field, Input } from '@/components'
import { toast } from '@/lib/toast'

export function ProfileForm({ initial }: { initial: Profile }) {
  const countries = useCountryOptions()
  const update = useUpdateProfile()
  const [fullName, setFullName] = useState(initial.full_name ?? '')
  const [residence, setResidence] = useState(initial.residence_country_code)
  const [citizenships, setCitizenships] = useState(() => {
    const primaryFirst = [...initial.citizenships].sort((a, b) => Number(b.is_primary) - Number(a.is_primary))
    return primaryFirst.map((c) => c.country_code)
  })
  const error = (field: string) => (update.error instanceof ApiError ? update.error.fieldError(field) : undefined)

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    update.mutate(
      {
        full_name: fullName.trim() || null,
        residence_country_code: residence,
        citizenships: citizenships.map((code, index) => ({ country_code: code, is_primary: index === 0 })),
      },
      {
        onSuccess: () => toast.success('Profile saved.'),
        onError: () => toast.error('Profile was not saved.'),
      },
    )
  }

  const options = countries.data ?? []

  return (
    <Card>
      <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
        <Field label="Full name" htmlFor="full-name" error={error('full_name')}>
          <Input id="full-name" maxLength={120} value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </Field>
        <Field label="Country of residence" htmlFor="residence" error={error('residence_country_code')}>
          <CountrySelect id="residence" options={options} value={residence} onChange={setResidence} />
        </Field>
        <div className="md:col-span-2">
          <Field
            label="Citizenships"
            htmlFor="citizenships"
            hint="The first one is your primary citizenship."
            error={error('citizenships')}
          >
            <CountryMultiSelect id="citizenships" options={options} value={citizenships} onChange={setCitizenships} />
          </Field>
        </div>
        <div className="flex items-center gap-3 md:col-span-2">
          <Button type="submit" disabled={update.isPending}>
            {update.isPending ? 'Saving…' : 'Save profile'}
          </Button>
          <span className="text-xs text-slate-500">Profile version {initial.profile_version}</span>
        </div>
      </form>
    </Card>
  )
}
