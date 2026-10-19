import { useState } from 'react'
import { ApiError } from '../../api/client.ts'
import { submitItem } from '../../api/items.ts'
import type { SubmitItemBody } from '../../api/types.ts'

type SubmitState =
  | { status: 'idle' }
  | { status: 'sending' }
  | { status: 'error'; message: string; problems: string[] }

type FieldProblem = { loc: (string | number)[]; message: string }

function problemsOf(error: ApiError): string[] {
  const fields = error.details?.fields
  if (!Array.isArray(fields)) return []
  return (fields as FieldProblem[]).map(
    (field) => `${String(field.loc[field.loc.length - 1])}: ${field.message}`,
  )
}

export function useSubmit(onDone: (body: SubmitItemBody) => void) {
  const [state, setState] = useState<SubmitState>({ status: 'idle' })

  async function submit(body: SubmitItemBody) {
    setState({ status: 'sending' })
    try {
      await submitItem(body)
      setState({ status: 'idle' })
      onDone(body)
    } catch (error) {
      if (error instanceof ApiError) {
        setState({ status: 'error', message: error.message, problems: problemsOf(error) })
      } else {
        setState({ status: 'error', message: 'Could not reach the server.', problems: [] })
      }
    }
  }

  return { state, submit }
}
