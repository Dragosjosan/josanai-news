export type Topic = {
  slug: string
  name: string
  description: string
  tags: string[]
}

export type VoteDirection = 'up'

export type FeedItem = {
  id: number
  title: string
  url: string
  domain: string
  topic: string
  tags: string[]
  score: number
  comment_count: number
  username: string | null
  label: string | null
  created_at: string
  viewer_vote: VoteDirection | null
}

export type SourceLink = {
  url: string
  domain: string
}

export type ItemRef = {
  id: number
  title: string
  domain: string
  created_at: string
}

export type ItemDetail = FeedItem & {
  source_name: string | null
  published_at: string | null
  summary: string | null
  primary_ref: string | null
  corroborating: SourceLink[]
  earlier: ItemRef[]
  later: ItemRef[]
  viewer_reported: boolean
}

export type VoteResult = {
  score: number
  viewer_vote: VoteDirection | null
}

export type Feed = {
  items: FeedItem[]
}

export type FeedFilters = {
  topic?: string
  tag?: string
}

export type SubmitItemBody = {
  url: string
  title: string
  topic: string
  tags: string[]
}

export type ErrorBody = {
  error: {
    code: string
    message: string
    details: Record<string, unknown> | null
  }
}
