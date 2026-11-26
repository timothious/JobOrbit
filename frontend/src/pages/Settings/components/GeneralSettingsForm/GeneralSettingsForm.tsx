import { useState, type FormEvent } from 'react'
import { ApiError, useSaveSettings, type AppSettings } from '@/api'
import { Button, Card, Field, Input, Select } from '@/components'
import { toast } from '@/lib/toast'

export function GeneralSettingsForm({ initial }: { initial: AppSettings }) {
  const [form, setForm] = useState(initial)
  const save = useSaveSettings()
  const error = (field: keyof AppSettings) =>
    save.error instanceof ApiError ? save.error.fieldError(field) : undefined

  const set = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => setForm({ ...form, [key]: value })

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    save.mutate(form, {
      onSuccess: () => toast.success('Settings saved.'),
      onError: () => toast.error('Settings were not saved. Check the highlighted fields.'),
    })
  }

  return (
    <Card>
      <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
        <Field label="Timezone" htmlFor="timezone" hint="IANA name, e.g. Europe/Berlin." error={error('timezone')}>
          <Input id="timezone" required value={form.timezone} onChange={(e) => set('timezone', e.target.value)} />
        </Field>
        <Field label="Display currency" htmlFor="display-currency" error={error('display_currency')}>
          <Input
            id="display-currency"
            required
            maxLength={3}
            value={form.display_currency}
            onChange={(e) => set('display_currency', e.target.value.toUpperCase())}
          />
        </Field>
        <Field
          label="Reference currency"
          htmlFor="reference-currency"
          hint="Used to compare salaries across currencies."
          error={error('reference_currency')}
        >
          <Input
            id="reference-currency"
            required
            maxLength={3}
            value={form.reference_currency}
            onChange={(e) => set('reference_currency', e.target.value.toUpperCase())}
          />
        </Field>
        <Field
          label="“New job” window (days)"
          htmlFor="new-job-window"
          hint="1–30 days."
          error={error('new_job_window_days')}
        >
          <Input
            id="new-job-window"
            type="number"
            min={1}
            max={30}
            required
            value={form.new_job_window_days}
            onChange={(e) => set('new_job_window_days', Number(e.target.value))}
          />
        </Field>
        <Field label="Default page size" htmlFor="page-size">
          <Select
            id="page-size"
            value={form.default_page_size}
            onChange={(e) => set('default_page_size', Number(e.target.value) as AppSettings['default_page_size'])}
          >
            {[20, 50, 100].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Default analytics period" htmlFor="analytics-period">
          <Select
            id="analytics-period"
            value={form.analytics_default_period_days}
            onChange={(e) =>
              set('analytics_default_period_days', Number(e.target.value) as AppSettings['analytics_default_period_days'])
            }
          >
            {[30, 90, 365].map((n) => (
              <option key={n} value={n}>
                {n} days
              </option>
            ))}
          </Select>
        </Field>
        <label className="flex items-center gap-2 text-sm text-slate-700 md:col-span-2">
          <input
            type="checkbox"
            className="size-4 accent-blue-600"
            checked={form.fx_auto_refresh}
            onChange={(e) => set('fx_auto_refresh', e.target.checked)}
          />
          Refresh exchange rates automatically
        </label>
        <div className="md:col-span-2">
          <Button type="submit" disabled={save.isPending}>
            {save.isPending ? 'Saving…' : 'Save settings'}
          </Button>
        </div>
      </form>
    </Card>
  )
}
