import { getJson, postJson } from './client.ts'
import type { Account, LoginBody } from './types.ts'

export function fetchMe(signal?: AbortSignal): Promise<Account | null> {
  return getJson<Account | null>('/auth/me', {}, signal)
}

export function login(body: LoginBody): Promise<Account> {
  return postJson<Account>('/auth/login', body)
}

export function logout(): Promise<void> {
  return postJson<void>('/auth/logout')
}
