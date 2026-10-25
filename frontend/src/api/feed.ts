import { getJson } from './client.ts'
import type { Feed, FeedQuery, SearchResult } from './types.ts'

export function fetchFeed(query: FeedQuery, signal?: AbortSignal): Promise<Feed> {
  return getJson<Feed>('/items', query, signal)
}

export function searchItems(q: string, page: number, signal?: AbortSignal): Promise<SearchResult> {
  return getJson<SearchResult>('/search', { q, page }, signal)
}
