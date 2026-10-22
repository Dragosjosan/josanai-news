import { getJson, postJson, putJson } from './client.ts'
import type { FeedItem, ItemDetail, SubmitItemBody, VoteResult } from './types.ts'

export function submitItem(body: SubmitItemBody): Promise<FeedItem> {
  return postJson<FeedItem>('/items', { contract_version: '1', ...body })
}

export function fetchItem(id: number, signal?: AbortSignal): Promise<ItemDetail> {
  return getJson<ItemDetail>(`/items/${id}`, {}, signal)
}

export function voteItem(id: number, direction: 'up' | 'none'): Promise<VoteResult> {
  return putJson<VoteResult>(`/items/${id}/vote`, { direction })
}
