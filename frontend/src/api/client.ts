import type { ApiErrorBody, ApiErrorDetail } from './types'

const BASE = '/api/v1'
const SAFE_METHODS = new Set(['GET', 'HEAD'])

let csrfToken: string | null = null

export function setCsrfToken(token: string | null) {
  csrfToken = token
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: ApiErrorDetail[]
  readonly requestId: string | null

  constructor(status: number, body: ApiErrorBody | null) {
    super(body?.error.message ?? `Request failed (${status})`)
    this.status = status
    this.code = body?.error.code ?? 'internal_error'
    this.details = body?.error.details ?? []
    this.requestId = body?.request_id ?? null
  }

  /** Message for one form field, if the server rejected it. */
  fieldError(field: string): string | undefined {
    return this.details.find((d) => d.field === field || d.field.startsWith(`${field}.`))?.message
  }
}

export async function api<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (!SAFE_METHODS.has(method) && csrfToken) headers['X-JobOrbit-CSRF'] = csrfToken

  const response = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'same-origin',
  })

  if (!response.ok) {
    const errorBody = (await response.json().catch(() => null)) as ApiErrorBody | null
    throw new ApiError(response.status, errorBody)
  }
  return (response.status === 204 ? undefined : await response.json()) as T
}
