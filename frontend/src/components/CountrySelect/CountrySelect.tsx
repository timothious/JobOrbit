import type { CountryOption } from '@/api'
import { Select } from '@/components/Select'

interface CountrySelectProps {
  id: string
  options: CountryOption[]
  value: string | null
  onChange: (code: string | null) => void
}

export function CountrySelect({ id, options, value, onChange }: CountrySelectProps) {
  return (
    <Select id={id} value={value ?? ''} onChange={(e) => onChange(e.target.value || null)}>
      <option value="">Not set</option>
      {options.map((c) => (
        <option key={c.code} value={c.code}>
          {c.name}
        </option>
      ))}
    </Select>
  )
}
