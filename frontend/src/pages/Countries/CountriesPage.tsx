import { Search } from 'lucide-react'
import { useParams, useSearchParams } from 'react-router'
import { useCountries } from '@/api'
import { Input, PageHeader, Pagination, Skeleton } from '@/components'
import { CountryDetailPanel } from './components/CountryDetailPanel'
import { CountryList } from './components/CountryList'

export function CountriesPage() {
  const { code } = useParams()
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const page = Math.max(1, Number(params.get('page')) || 1)
  const countries = useCountries({ q, page })

  const update = (changes: Record<string, string | null>) =>
    setParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        Object.entries(changes).forEach(([k, v]) => (v ? next.set(k, v) : next.delete(k)))
        return next
      },
      { replace: true },
    )

  return (
    <>
      <PageHeader title="Country Explorer" description="Compare countries by opportunity and pathways." />
      <div className="relative mb-4 max-w-sm">
        <Search size={16} strokeWidth={1.75} aria-hidden="true" className="absolute top-2.5 left-3 text-slate-400" />
        <Input
          id="country-search"
          type="search"
          aria-label="Search countries"
          placeholder="Search countries"
          className="pl-9"
          value={q}
          onChange={(e) => update({ q: e.target.value || null, page: null })}
        />
      </div>
      <div className={`grid gap-4 ${code ? 'lg:grid-cols-[1fr_20rem]' : ''}`}>
        <div>
          {countries.isPending && <Skeleton className="h-96 w-full" />}
          {countries.isError && <p className="text-sm text-red-600">Countries could not be loaded.</p>}
          {countries.data && (
            <>
              {countries.data.items.length ? (
                <CountryList countries={countries.data.items} selected={code?.toUpperCase()} />
              ) : (
                <p className="text-sm text-slate-600">No countries match “{q}”.</p>
              )}
              <Pagination
                page={countries.data.page}
                totalPages={countries.data.total_pages}
                total={countries.data.total}
                onChange={(p) => update({ page: p > 1 ? String(p) : null })}
              />
            </>
          )}
        </div>
        {code && <CountryDetailPanel code={code.toUpperCase()} />}
      </div>
    </>
  )
}
