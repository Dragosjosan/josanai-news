import type { FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router'
import type { SubmitItemBody } from '../../api/types.ts'
import { paths } from '../../routes/paths.ts'
import { useSubmit } from './useSubmit.ts'
import './SubmitPage.css'

function bodyFrom(form: FormData): SubmitItemBody {
  const text = (name: string) => String(form.get(name) ?? '').trim()
  return {
    url: text('url'),
    title: text('title'),
  }
}

function SubmitPage() {
  const [params] = useSearchParams()
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

      {state.status === 'error' && (
        <div className="alert alert-danger" role="alert">
          <div className="alert-content">
            <p>{state.message}</p>
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
