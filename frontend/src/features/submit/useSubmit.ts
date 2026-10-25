import { useState } from 'react'
import { ApiError } from '../../api/client.ts'
import { submitItem } from '../../api/items.ts'
import type { SubmitItemBody } from '../../api/types.ts'

export type Existing = { id: number; title: string; url: string }

type SubmitState =
  | { status: 'idle' }
  | { status: 'sending' }
  | { status: 'error'; message: string; problems: string[]; existing: Existing | null }

type FieldProblem = { loc: (string | number)[]; message: string }

function problemsOf(error: ApiError): string[] {
  const fields = error.details?.fields
  if (!Array.isArray(fields)) return []
  return (fields as FieldProblem[]).map(
    (field) => `${String(field.loc[field.loc.length - 1])}: ${field.message}`,
  )
}

function existingOf(error: ApiError): Existing | null {
  const details = error.details
  if (error.code !== 'duplicate' || typeof details?.item_id !== 'number') return null
  return { id: details.item_id, title: String(details.title), url: String(details.url) }
}

export function useSubmit(onDone: () => void) {
  const [state, setState] = useState<SubmitState>({ status: 'idle' })

  async function submit(body: SubmitItemBody) {
    setState({ status: 'sending' })
    try {
      await submitItem(body)
      setState({ status: 'idle' })
      onDone()
    } catch (error) {
      if (error instanceof ApiError) {
        setState({
          status: 'error',
          message: error.message,
          problems: problemsOf(error),
          existing: existingOf(error),
        })
      } else {
        setState({ status: 'error', message: 'Could not reach the server.', problems: [], existing: null })
      }
    }
  }

  return { state, submit }
}
