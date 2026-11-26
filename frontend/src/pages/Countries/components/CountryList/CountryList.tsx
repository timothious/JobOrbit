import { Link } from 'react-router'
import type { CountryListItem } from '@/api'

const ENGLISH_STATUS: Record<CountryListItem['english_status'], string> = {
  official: 'Official',
  widely_used_in_business: 'Widely used in business',
  limited: 'Limited',
  unknown: 'Unknown',
}

export function CountryList({ countries, selected }: { countries: CountryListItem[]; selected?: string }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs font-medium text-slate-600 uppercase">
          <tr>
            <th scope="col" className="px-3 py-2">Country</th>
            <th scope="col" className="hidden px-3 py-2 sm:table-cell">Region</th>
            <th scope="col" className="hidden px-3 py-2 md:table-cell">Currency</th>
            <th scope="col" className="px-3 py-2">English</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {countries.map((c) => (
            <tr key={c.code} className={c.code === selected ? 'bg-blue-50' : 'hover:bg-slate-50'}>
              <td className="px-3 py-2">
                <Link to={`/countries/${c.code}`} className="font-medium text-blue-700 hover:underline">
                  {c.name}
                </Link>
              </td>
              <td className="hidden px-3 py-2 text-slate-700 sm:table-cell">{c.subregion ?? c.region ?? '—'}</td>
              <td className="hidden px-3 py-2 text-slate-700 tabular-nums md:table-cell">{c.currency_code ?? '—'}</td>
              <td className="px-3 py-2 text-slate-700">{ENGLISH_STATUS[c.english_status]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
