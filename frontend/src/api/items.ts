import { postJson } from './client.ts'
import type { FeedItem, SubmitItemBody } from './types.ts'

export function submitItem(body: SubmitItemBody): Promise<FeedItem> {
  return postJson<FeedItem>('/items', { contract_version: '1', ...body })
}
