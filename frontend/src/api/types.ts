// Mirrors the backend schemas (API Specification §1–§15). Keep in sync with /openapi.json.

export interface ApiErrorDetail {
  field: string
  code: string
  message: string
}

export interface ApiErrorBody {
  error: { code: string; message: string; details?: ApiErrorDetail[] }
  request_id: string | null
}

export interface Page<T> {
  items: T[]
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface AuthStatus {
  setup_complete: boolean
  authenticated: boolean
}

export interface SessionInfo {
  csrf_token: string
  expires_at: string
}

export interface SetupRequest {
  password: string
  profile: {
    full_name: string | null
    citizenship_country_codes: string[]
    residence_country_code: string | null
  }
  timezone: string
}

export interface AppSettings {
  timezone: string
  display_currency: string
  reference_currency: string
  new_job_window_days: number
  default_page_size: 20 | 50 | 100
  analytics_default_period_days: 30 | 90 | 365
  fx_auto_refresh: boolean
  retention: Record<string, number>
  freshness: { pathway_fresh_days: number; pathway_outdated_days: number }
}

export interface Citizenship {
  country_code: string
  is_primary: boolean
}

export interface Profile {
  full_name: string | null
  residence_country_code: string | null
  citizenships: Citizenship[]
  profile_version: number
  updated_at: string
}

export type ProfilePatch = Partial<Pick<Profile, 'full_name' | 'residence_country_code' | 'citizenships'>>

export interface CountryOption {
  code: string
  name: string
}

export interface CountryListItem extends CountryOption {
  region: string | null
  subregion: string | null
  currency_code: string | null
  english_status: 'official' | 'widely_used_in_business' | 'limited' | 'unknown'
  english_status_verified_at: string | null
}

export interface CountryDetail extends CountryListItem {
  iso3: string
  official_name: string | null
  languages: string[]
  region_codes: string[]
}
