import { useEffect, useState } from 'react'
import { fetchFeed } from '../../api/feed.ts'
import type { FeedItem } from '../../api/types.ts'

export type FeedState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; items: FeedItem[] }

export function useFeed(sort: 'top' | 'new', day?: string) {
  const [state, setState] = useState<FeedState>({ status: 'loading' })

  const key = `${sort}|${day ?? ''}`
  const [loadedKey, setLoadedKey] = useState(key)
  if (loadedKey !== key) {
    setLoadedKey(key)
    setState({ status: 'loading' })
  }

  useEffect(() => {
    const controller = new AbortController()
    fetchFeed({ sort, day }, controller.signal)
      .then((feed) => setState({ status: 'ready', items: feed.items }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ status: 'error', error })
      })
    return () => controller.abort()
  }, [sort, day])

  return state
}
