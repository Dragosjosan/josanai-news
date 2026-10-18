export type Topic = {
  slug: string
  name: string
  tags: string[]
  remaining_today: number
}

export type FeedItem = {
  id: number
  title: string
  url: string
  domain: string
  topic: string
  tags: string[]
  score: number
  comment_count: number
  submitted_by: string | null
  created_at: string
}

export type Feed = {
  items: FeedItem[]
}

export type FeedFilters = {
  topic?: string
  tag?: string
}
