import { X } from 'lucide-react'
import type { CountryOption } from '@/api'
import { Select } from '@/components/Select'

interface CountryMultiSelectProps {
  id: string
  options: CountryOption[]
  /** Selected country codes; the first one is the primary. */
  value: string[]
  onChange: (codes: string[]) => void
}

export function CountryMultiSelect({ id, options, value, onChange }: CountryMultiSelectProps) {
  const names = new Map(options.map((c) => [c.code, c.name]))

  return (
    <div className="space-y-2">
      {value.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {value.map((code, index) => (
            <li
              key={code}
              className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-slate-50 py-1 pr-1 pl-2 text-sm"
            >
              {names.get(code) ?? code}
              {index === 0 && <span className="text-xs text-slate-500">(primary)</span>}
              <button
                type="button"
                onClick={() => onChange(value.filter((c) => c !== code))}
                aria-label={`Remove ${names.get(code) ?? code}`}
                className="rounded p-0.5 text-slate-500 hover:bg-slate-200"
              >
                <X size={14} strokeWidth={1.75} aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
      <Select id={id} value="" onChange={(e) => e.target.value && onChange([...value, e.target.value])}>
        <option value="">Add a country…</option>
        {options
          .filter((c) => !value.includes(c.code))
          .map((c) => (
            <option key={c.code} value={c.code}>
              {c.name}
            </option>
          ))}
      </Select>
    </div>
  )
}
