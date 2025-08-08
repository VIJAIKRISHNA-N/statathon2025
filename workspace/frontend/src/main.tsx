import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App'
import UploadPage from './pages/UploadPage'
import DatasetPage from './pages/DatasetPage'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/upload', element: <UploadPage /> },
  { path: '/datasets/:id', element: <DatasetPage /> },
])

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>,
)
