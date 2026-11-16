import { useId, useState, type FormEvent } from 'react'
import { ApiError } from '../../../api/client.ts'
import { editItem } from '../../../api/items.ts'
import type { ItemDetail } from '../../../api/types.ts'

const MAX_TITLE = 300
const MAX_SUMMARY = 1000

type Props = {
  item: ItemDetail
  onSaved: (item: ItemDetail) => void
  onCancel: () => void
}

function EditItemForm({ item, onSaved, onCancel }: Props) {
  const id = useId()
  const [title, setTitle] = useState(item.title)
  const [summary, setSummary] = useState(item.summary ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const summaryLength = Array.from(summary).length
  const invalid = !title.trim() || summaryLength > MAX_SUMMARY

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (saving || invalid) return
    setSaving(true)
    setError(null)
    try {
      onSaved(await editItem(item.id, { title, summary: summary.trim() ? summary : null }))
    } catch (failure) {
      setError(failure instanceof ApiError ? failure.message : 'Could not reach the server. Try again.')
      setSaving(false)
    }
  }

  return (
    <form className="item-edit-form stack" onSubmit={(event) => void save(event)} aria-busy={saving}>
      <div className="field">
        <label className="field-label" htmlFor={`${id}-title`}>title</label>
        <input
          className="input"
          id={`${id}-title`}
          required
          maxLength={MAX_TITLE}
          value={title}
          readOnly={saving}
          onChange={(event) => setTitle(event.currentTarget.value)}
        />
      </div>

      <div className="field">
        <label className="field-label" htmlFor={`${id}-summary`}>summary</label>
        <textarea
          className="input"
          id={`${id}-summary`}
          rows={6}
          value={summary}
          readOnly={saving}
          aria-invalid={summaryLength > MAX_SUMMARY || undefined}
          aria-describedby={`${id}-count`}
          onChange={(event) => setSummary(event.currentTarget.value)}
        />
        <p className="field-help" id={`${id}-count`}>
          {summaryLength}/{MAX_SUMMARY} characters. Saving marks the story as edited.
        </p>
      </div>

      <div className="item-edit-actions">
        <button className="btn btn-primary btn-compact" type="submit" disabled={saving || invalid}>
          {saving ? 'saving…' : 'save'}
        </button>
        <button className="btn btn-ghost btn-compact" type="button" onClick={onCancel} disabled={saving}>
          cancel
        </button>
        {error && <span className="item-edit-error" role="alert">{error}</span>}
      </div>
    </form>
  )
}

export default EditItemForm
