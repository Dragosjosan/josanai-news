import { RouterProvider } from 'react-router'
import { router } from '../routes/router.tsx'
import AuthProvider from './AuthProvider.tsx'

function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )
}

export default App
