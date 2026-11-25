import { SearchX } from 'lucide-react'
import { Button, EmptyState } from '@/components'

export function NotFoundPage() {
  return (
    <>
      <title>Page not found · JobOrbit</title>
      <EmptyState
        icon={SearchX}
        title="Page not found"
        description="The page you are looking for does not exist."
        action={<Button to="/">Go to dashboard</Button>}
      />
    </>
  )
}
