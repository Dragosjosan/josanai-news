import { useEffect, useState, type ReactNode } from 'react'
import { fetchMe } from '../api/auth.ts'
import type { Account } from '../api/types.ts'
import { AuthContext } from './authContext.ts'

function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    fetchMe(controller.signal)
      .then(setAccount)
      .catch(() => undefined)
    return () => controller.abort()
  }, [])

  return <AuthContext value={{ account, setAccount }}>{children}</AuthContext>
}

export default AuthProvider
