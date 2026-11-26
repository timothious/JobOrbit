import { useSyncExternalStore } from 'react'

export interface Toast {
  id: number
  kind: 'success' | 'error'
  message: string
}

const DURATION_MS = 4000
let toasts: Toast[] = []
let nextId = 1
const listeners = new Set<() => void>()

function emit() {
  listeners.forEach((listener) => listener())
}

export function dismissToast(id: number) {
  toasts = toasts.filter((t) => t.id !== id)
  emit()
}

function show(kind: Toast['kind'], message: string) {
  const id = nextId++
  toasts = [...toasts, { id, kind, message }]
  emit()
  setTimeout(() => dismissToast(id), DURATION_MS)
}

export const toast = {
  success: (message: string) => show('success', message),
  error: (message: string) => show('error', message),
}

export function useToasts() {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener)
      return () => {
        listeners.delete(listener)
      }
    },
    () => toasts,
  )
}
