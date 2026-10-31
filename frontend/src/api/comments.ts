import { deleteJson, getJson, postJson } from './client.ts'
import type { Comment, CommentThread, SubmitCommentBody } from './types.ts'

export function fetchComments(itemId: number, signal?: AbortSignal): Promise<CommentThread> {
  return getJson<CommentThread>(`/items/${itemId}/comments`, {}, signal)
}

export function submitComment(itemId: number, body: SubmitCommentBody): Promise<Comment> {
  return postJson<Comment>(`/items/${itemId}/comments`, body)
}

export function deleteComment(id: number): Promise<void> {
  return deleteJson(`/comments/${id}`)
}
