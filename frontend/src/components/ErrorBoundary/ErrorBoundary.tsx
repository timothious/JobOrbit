import { TriangleAlert } from 'lucide-react'
import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'

interface ErrorBoundaryProps {
  children: ReactNode
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack)
  }

  render() {
    if (!this.state.failed) return this.props.children

    return (
      <EmptyState
        icon={TriangleAlert}
        title="Something went wrong"
        description="This page failed to load. Reloading usually fixes it."
        action={<Button onClick={() => window.location.reload()}>Reload</Button>}
      />
    )
  }
}
