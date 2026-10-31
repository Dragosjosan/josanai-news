import { useState, type CSSProperties } from 'react'
import type { Comment } from '../../api/types.ts'
import { ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import { timeAgo } from '../../lib/format.ts'
import CommentForm from './CommentForm.tsx'
import type { useComments } from './useComments.ts'
import './Comments.css'

type Discussion = ReturnType<typeof useComments>
type ThreadRow = { comment: Comment; depth: number }

function threadRows(comments: Comment[]): ThreadRow[] {
  const ids = new Set(comments.map((comment) => comment.id))
  const children = new Map<number | null, Comment[]>()
  for (const comment of comments) {
    const parent = comment.parent_id !== null && ids.has(comment.parent_id) ? comment.parent_id : null
    const siblings = children.get(parent) ?? []
    siblings.push(comment)
    children.set(parent, siblings)
  }
  const rows: ThreadRow[] = []
  const stack = (children.get(null) ?? []).toReversed().map((comment) => ({ comment, depth: 0 }))
  while (stack.length > 0) {
    const row = stack.pop()!
    rows.push(row)
    for (const comment of (children.get(row.comment.id) ?? []).toReversed()) {
      stack.push({ comment, depth: row.depth + 1 })
    }
  }
  return rows
}

function CommentEntry({ comment, depth, discussion }: ThreadRow & { discussion: Discussion }) {
  const [replying, setReplying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function remove() {
    setError(null)
    try {
      await discussion.remove(comment.id)
      setReplying(false)
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Could not delete this comment.')
    }
  }

  return (
    <li
      className="comment-entry"
      id={`comment-${comment.id}`}
      style={{ '--comment-depth': Math.min(depth, 6) } as CSSProperties}
    >
      <div className="comment-meta">
        {comment.author && <span className="comment-author">{comment.author}</span>}
        <a className="comment-time" href={`#comment-${comment.id}`}>
          <time dateTime={comment.created_at} title={new Date(comment.created_at).toLocaleString()}>
            {timeAgo(comment.created_at)}
          </time>
        </a>
        {!comment.deleted && (
          <>
            <span className="comment-separator" aria-hidden="true">|</span>
            <button
              className="comment-action"
              type="button"
              aria-expanded={replying}
              aria-controls={`reply-${comment.id}`}
              disabled={discussion.pending}
              onClick={() => setReplying((current) => !current)}
            >reply</button>
            {comment.can_delete && (
              <>
                <span className="comment-separator" aria-hidden="true">|</span>
                <button
                  className="comment-action comment-delete"
                  type="button"
                  disabled={discussion.pending}
                  onClick={() => void remove()}
                >delete</button>
              </>
            )}
          </>
        )}
      </div>
      <p className={`comment-text${comment.deleted ? ' comment-deleted' : ''}`}>
        {comment.deleted ? '[deleted]' : comment.text}
      </p>
      {error && <p className="comment-error" role="alert">{error}</p>}
      <div id={`reply-${comment.id}`} hidden={!replying || comment.deleted}>
        {replying && !comment.deleted && (
          <CommentForm
            reply
            busy={discussion.pending}
            onSubmit={(text) => discussion.add(text, comment.id)}
            onDone={() => setReplying(false)}
            onCancel={() => setReplying(false)}
          />
        )}
      </div>
    </li>
  )
}

function Comments({ discussion }: { discussion: Discussion }) {
  const { state } = discussion

  return (
    <section className="comments" aria-label="Discussion">
      {state.status === 'loading' && <LoadingState label="Loading comments" />}
      {state.status === 'error' && (
        <>
          <ErrorState title="Could not load comments." error={state.error} />
          <button className="btn btn-ghost btn-compact" type="button" onClick={discussion.reload}>retry</button>
        </>
      )}
      {state.status === 'ready' && (
        <>
          <CommentForm busy={discussion.pending} onSubmit={(text) => discussion.add(text, null)} />
          <ol className="comment-list">
            {threadRows(state.comments).map(({ comment, depth }) => (
              <CommentEntry key={comment.id} comment={comment} depth={depth} discussion={discussion} />
            ))}
          </ol>
        </>
      )}
    </section>
  )
}

export default Comments
