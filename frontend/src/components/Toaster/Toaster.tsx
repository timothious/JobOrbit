import { CircleAlert, CircleCheck, X } from 'lucide-react'
import { dismissToast, useToasts } from '@/lib/toast'

export function Toaster() {
  const toasts = useToasts()

  return (
    <div aria-live="polite" className="fixed inset-x-4 bottom-20 z-50 flex flex-col items-center gap-2 md:right-4 md:bottom-4 md:left-auto md:items-end">
      {toasts.map(({ id, kind, message }) => {
        const Icon = kind === 'success' ? CircleCheck : CircleAlert
        return (
          <div
            key={id}
            role={kind === 'error' ? 'alert' : 'status'}
            className="flex w-full max-w-sm items-start gap-2 rounded-lg border border-slate-200 bg-white p-3 text-sm shadow-lg"
          >
            <Icon
              size={16}
              strokeWidth={1.75}
              aria-hidden="true"
              className={`mt-0.5 shrink-0 ${kind === 'success' ? 'text-green-600' : 'text-red-600'}`}
            />
            <p className="flex-1 text-slate-800">{message}</p>
            <button type="button" onClick={() => dismissToast(id)} aria-label="Dismiss" className="text-slate-500">
              <X size={16} strokeWidth={1.75} aria-hidden="true" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
