import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import type { SubmitItemBody } from '../../api/types.ts'
import { itemUrl, paths } from '../../routes/paths.ts'
import { useSubmit } from './useSubmit.ts'
import './SubmitPage.css'

function bodyFrom(form: FormData): SubmitItemBody {
  const text = (name: string) => String(form.get(name) ?? '').trim()
  return {
    url: text('url'),
    title: text('title'),
    summary: text('summary') || null,
  }
}

function SubmitPage() {
  const [params] = useSearchParams()
  const [summary, setSummary] = useState(params.get('summary') ?? '')
  const navigate = useNavigate()
  const { state, submit } = useSubmit(() => navigate(paths.newest))

  return (
    <form
      className="submit-form stack"
      onSubmit={(event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        void submit(bodyFrom(new FormData(event.currentTarget)))
      }}
    >
      <div className="field">
        <label className="field-label" htmlFor="url">
          url
        </label>
        <input className="input" id="url" name="url" type="url" required defaultValue={params.get('url') ?? ''} />
      </div>

      <div className="field">
        <label className="field-label" htmlFor="title">
          title
        </label>
        <input className="input" id="title" name="title" required maxLength={300} defaultValue={params.get('title') ?? ''} />
      </div>

      <div className="field">
        <label className="field-label" htmlFor="summary">
          summary (optional)
        </label>
        <textarea
          className="input"
          id="summary"
          name="summary"
          maxLength={500}
          aria-describedby="summary-help"
          value={summary}
          onChange={(event) => setSummary(event.currentTarget.value)}
        />
        <p className="field-help" id="summary-help">{summary.length}/500 characters</p>
      </div>

      {state.status === 'error' && (
        <div className="alert alert-danger" role="alert">
          <div className="alert-content">
            <p>{state.message}</p>
            {state.existing && (
              <p>
                <Link to={itemUrl(state.existing.id)}>{state.existing.title}</Link>
                <span className="submit-existing-url"> {state.existing.url}</span>
              </p>
            )}
            {state.problems.map((problem) => (
              <p key={problem}>{problem}</p>
            ))}
          </div>
        </div>
      )}

      <div>
        <button type="submit" className="btn btn-primary" disabled={state.status === 'sending'}>
          submit
        </button>
      </div>
    </form>
  )
}

export default SubmitPage
