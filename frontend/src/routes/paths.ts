import type { FeedFilters } from '../api/types.ts'

export const paths = {
  home: '/',
  submit: '/submit',
  item: '/item/:id',
} as const

export function itemUrl(id: number): string {
  return `/item/${id}`
}

export function feedUrl({ topic, tag }: FeedFilters = {}): string {
  const params = new URLSearchParams()
  if (topic) params.set('topic', topic)
  if (tag) params.set('tag', tag)
  const qs = params.toString()
  return qs ? `${paths.home}?${qs}` : paths.home
}
