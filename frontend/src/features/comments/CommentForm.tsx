import { useId, useState, type FormEvent } from 'react'
import { ApiError } from '../../api/client.ts'

type Props = {
  reply?: boolean
  busy: boolean
  onSubmit: (text: string) => Promise<void>
  onDone?: () => void
  onCancel?: () => void
}

function CommentForm({ reply = false, busy, onSubmit, onDone, onCancel }: Props) {
  const id = useId()
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const length = Array.from(draft).length
  const tooLong = length > 5000

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy || !draft.trim() || tooLong) return
    setSending(true)
    setError(null)
    try {
      await onSubmit(draft)
      setDraft('')
      onDone?.()
    } catch (failure) {
      setError(failure instanceof ApiError ? failure.message : 'Could not reach the server. Try again.')
    } finally {
      setSending(false)
    }
  }

  return (
    <form className="comment-form" onSubmit={(event) => void submit(event)} aria-busy={sending}>
      <label className="field-label" htmlFor={id}>{reply ? 'reply' : 'add a comment'}</label>
      <textarea
        className="input comment-input"
        id={id}
        name="text"
        rows={reply ? 3 : 5}
        placeholder={reply ? 'Reply' : 'Add a comment'}
        required
        value={draft}
        readOnly={sending}
        aria-invalid={tooLong || undefined}
        aria-describedby={`${id}-count${error ? ` ${id}-error` : ''}`}
        onChange={(event) => setDraft(event.currentTarget.value)}
      />
      <div className="comment-form-actions">
        <button className="btn btn-primary btn-compact" type="submit" disabled={busy || !draft.trim() || tooLong}>
          {sending ? 'posting…' : reply ? 'reply' : 'add comment'}
        </button>
        {onCancel && (
          <button className="btn btn-ghost btn-compact" type="button" onClick={onCancel} disabled={busy}>cancel</button>
        )}
        <span className={`comment-counter${tooLong ? ' comment-error' : ''}`} id={`${id}-count`}>
          {length}/5000 characters
        </span>
      </div>
      {error && <p className="comment-error" id={`${id}-error`} role="alert">{error}</p>}
    </form>
  )
}

export default CommentForm
