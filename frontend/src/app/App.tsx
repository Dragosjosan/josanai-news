import { RouterProvider } from 'react-router'
import { router } from '../routes/router.tsx'
import AuthProvider from './AuthProvider.tsx'
import TopicsProvider from './TopicsProvider.tsx'

function App() {
  return (
    <AuthProvider>
      <TopicsProvider>
        <RouterProvider router={router} />
      </TopicsProvider>
    </AuthProvider>
  )
}

export default App
