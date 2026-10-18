import { useEffect, useState } from 'react'
import { fetchFeed } from '../../api/feed.ts'
import type { FeedFilters, FeedItem } from '../../api/types.ts'

type FeedState = {
  items: FeedItem[]
  status: 'loading' | 'idle' | 'error'
  error: Error | null
}

const INITIAL: FeedState = { items: [], status: 'loading', error: null }

export function useFeed({ topic, tag }: FeedFilters) {
  const [state, setState] = useState<FeedState>(INITIAL)

  const filterKey = `${topic ?? ''}|${tag ?? ''}`
  const [loadedKey, setLoadedKey] = useState(filterKey)
  if (loadedKey !== filterKey) {
    setLoadedKey(filterKey)
    setState(INITIAL)
  }

  useEffect(() => {
    const controller = new AbortController()
    fetchFeed({ topic, tag }, controller.signal)
      .then((feed) => setState({ items: feed.items, status: 'idle', error: null }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ items: [], status: 'error', error })
      })
    return () => controller.abort()
  }, [topic, tag])

  return state
}
