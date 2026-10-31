import { useEffect, useState } from 'react'
import { deleteComment, fetchComments, submitComment } from '../../api/comments.ts'
import type { Comment } from '../../api/types.ts'
import { useAuth } from '../../app/authContext.ts'

type CommentState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; comments: Comment[] }

export function useComments(itemId: number) {
  const { account } = useAuth()
  const [state, setState] = useState<CommentState>({ status: 'loading' })
  const [pending, setPending] = useState(false)
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    fetchComments(itemId, controller.signal)
      .then((thread) => setState({ status: 'ready', comments: thread.comments }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ status: 'error', error })
      })
    return () => controller.abort()
  }, [itemId, account?.id, revision])

  async function add(text: string, parentId: number | null) {
    setPending(true)
    try {
      const comment = await submitComment(itemId, { text, parent_id: parentId })
      setState((current) => current.status === 'ready'
        ? { ...current, comments: [...current.comments, comment] }
        : current)
    } finally {
      setPending(false)
    }
  }

  async function remove(id: number) {
    setPending(true)
    try {
      await deleteComment(id)
      setState((current) => current.status === 'ready'
        ? {
            ...current,
            comments: current.comments.map((comment) => comment.id === id
              ? { ...comment, deleted: true, author: null, text: null }
              : comment),
          }
        : current)
    } finally {
      setPending(false)
    }
  }

  function reload() {
    setState({ status: 'loading' })
    setRevision((current) => current + 1)
  }

  return { state, pending, add, remove, reload }
}
