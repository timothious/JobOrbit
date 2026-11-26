/** Only follow same-app paths after login, never another origin (open-redirect guard). */
export function safeNext(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/'
}
