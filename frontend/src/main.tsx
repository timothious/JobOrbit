import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import { createQueryClient } from '@/api'
import { Toaster } from '@/components'
import { UpdatePrompt } from '@/components/UpdatePrompt'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={createQueryClient()}>
      <BrowserRouter>
        <App />
        <Toaster />
        <UpdatePrompt />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
