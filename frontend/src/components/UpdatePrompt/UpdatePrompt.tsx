import { RefreshCw } from 'lucide-react'
import { useRegisterSW } from 'virtual:pwa-register/react'
import { Button } from '@/components/Button'

/** Shows "New version available" when a new service worker is waiting (T1.9). */
export function UpdatePrompt() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW()

  if (!needRefresh) return null

  return (
    <div
      role="status"
      className="fixed inset-x-4 top-4 z-50 mx-auto flex max-w-sm items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 text-sm shadow-lg"
    >
      <RefreshCw size={16} strokeWidth={1.75} aria-hidden="true" className="text-blue-600" />
      <p className="flex-1">New version available.</p>
      <Button onClick={() => updateServiceWorker(true)}>Reload</Button>
    </div>
  )
}
