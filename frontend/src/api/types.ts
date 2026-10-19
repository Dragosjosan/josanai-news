export type Topic = {
  slug: string
  name: string
  description: string
  tags: string[]
}

export type VoteDirection = 'up' | 'down'

export type FeedItem = {
  id: number
  title: string
  url: string
  domain: string
  topic: string
  tags: string[]
  score: number
  comment_count: number
  publisher: string | null
  created_at: string
  viewer_vote: VoteDirection | null
}

export type Feed = {
  items: FeedItem[]
}

export type FeedFilters = {
  topic?: string
  tag?: string
}

export type ErrorBody = {
  error: {
    code: string
    message: string
    details: Record<string, unknown> | null
  }
}
