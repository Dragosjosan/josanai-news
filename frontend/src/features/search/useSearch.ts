import { useEffect, useState } from 'react'
import { searchItems } from '../../api/feed.ts'
import type { FeedState } from '../feed/useFeed.ts'

export type SearchState = { feed: FeedState; hasMore: boolean }

export function useSearch(q: string, page: number) {
  const [state, setState] = useState<SearchState>({ feed: { status: 'loading' }, hasMore: false })

  const key = `${q}|${page}`
  const [loadedKey, setLoadedKey] = useState(key)
  if (loadedKey !== key) {
    setLoadedKey(key)
    setState({ feed: { status: 'loading' }, hasMore: false })
  }

  useEffect(() => {
    const controller = new AbortController()
    searchItems(q, page, controller.signal)
      .then((result) =>
        setState({ feed: { status: 'ready', items: result.items }, hasMore: result.has_more }),
      )
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ feed: { status: 'error', error }, hasMore: false })
      })
    return () => controller.abort()
  }, [q, page])

  return state
}
