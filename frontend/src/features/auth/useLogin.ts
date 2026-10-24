import { useState } from 'react'
import { login } from '../../api/auth.ts'
import { ApiError } from '../../api/client.ts'
import type { Account, LoginBody } from '../../api/types.ts'

type LoginState = { status: 'idle' } | { status: 'sending' } | { status: 'error'; message: string }

export function useLogin(onDone: (account: Account) => void) {
  const [state, setState] = useState<LoginState>({ status: 'idle' })

  async function submit(body: LoginBody) {
    setState({ status: 'sending' })
    try {
      const account = await login(body)
      setState({ status: 'idle' })
      onDone(account)
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Could not reach the server.'
      setState({ status: 'error', message })
    }
  }

  return { state, submit }
}
