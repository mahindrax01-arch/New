import React from 'react'
import ReactDOM from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'

import App from './App'
import { AuthProvider } from './context/AuthContext'
import './styles.css'

const clerkKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

const app = (
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
)

ReactDOM.createRoot(document.getElementById('root')!).render(
  clerkKey ? <ClerkProvider publishableKey={clerkKey}>{app}</ClerkProvider> : app
)
