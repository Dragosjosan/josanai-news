import { createContext, useContext } from 'react'
import type { Account } from '../api/types.ts'

export type AuthState = {
  account: Account | null
  setAccount: (account: Account | null) => void
}

export const AuthContext = createContext<AuthState>({ account: null, setAccount: () => undefined })

export function useAuth(): AuthState {
  return useContext(AuthContext)
}
