import { useEffect, useState } from 'react'
import { fetchItem } from '../../api/items.ts'
import type { ItemDetail } from '../../api/types.ts'

type ItemState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; item: ItemDetail }

export function useItem(id: number) {
  const [state, setState] = useState<ItemState>({ status: 'loading' })

  const [loadedId, setLoadedId] = useState(id)
  if (loadedId !== id) {
    setLoadedId(id)
    setState({ status: 'loading' })
  }

  useEffect(() => {
    const controller = new AbortController()
    fetchItem(id, controller.signal)
      .then((item) => setState({ status: 'ready', item }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ status: 'error', error })
      })
    return () => controller.abort()
  }, [id])

  return state
}
