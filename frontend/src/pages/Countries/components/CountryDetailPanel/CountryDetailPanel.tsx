import { X } from 'lucide-react'
import { Link } from 'react-router'
import { useCountry } from '@/api'
import { Card, Skeleton } from '@/components'

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 py-1.5">
      <dt className="text-slate-600">{label}</dt>
      <dd className="text-right text-slate-900">{value}</dd>
    </div>
  )
}

export function CountryDetailPanel({ code }: { code: string }) {
  const country = useCountry(code)

  return (
    <Card className="h-fit">
      <div className="flex items-start justify-between gap-2">
        <h2 className="text-base font-semibold">{country.data?.name ?? code}</h2>
        <Link to="/countries" aria-label="Close details" className="rounded-md p-1 text-slate-500 hover:bg-slate-100">
          <X size={16} strokeWidth={1.75} aria-hidden="true" />
        </Link>
      </div>
      {country.isPending && <Skeleton className="mt-3 h-32 w-full" />}
      {country.isError && <p className="mt-3 text-sm text-red-600">Country not found.</p>}
      {country.data && (
        <>
          {country.data.official_name && <p className="text-sm text-slate-600">{country.data.official_name}</p>}
          <dl className="mt-3 divide-y divide-slate-100 text-sm">
            <Row label="Region" value={[country.data.region, country.data.subregion].filter(Boolean).join(' · ') || '—'} />
            <Row label="Currency" value={country.data.currency_code ?? '—'} />
            <Row label="Official languages" value={country.data.languages.join(', ').toUpperCase() || '—'} />
            <Row label="Groups" value={country.data.region_codes.join(', ') || '—'} />
            <Row label="English status" value={country.data.english_status === 'unknown' ? 'Unknown' : country.data.english_status} />
          </dl>
          <p className="mt-3 text-xs text-slate-500">
            Jobs, salaries, pathways and scores for this country appear once sources are synced and pathways are added.
          </p>
        </>
      )}
    </Card>
  )
}
