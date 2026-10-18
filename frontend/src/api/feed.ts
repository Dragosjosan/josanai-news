import { getJson } from './client.ts'
import type { Feed, FeedFilters, Topic } from './types.ts'

export function fetchFeed(filters: FeedFilters, signal?: AbortSignal): Promise<Feed> {
  return getJson<Feed>('/items', filters, signal)
}

export function fetchTopics(signal?: AbortSignal): Promise<Topic[]> {
  return getJson<Topic[]>('/topics', {}, signal)
}
