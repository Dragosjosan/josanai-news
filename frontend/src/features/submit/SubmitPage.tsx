import type { FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router'
import type { SubmitItemBody } from '../../api/types.ts'
import { ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import { useTopics } from '../../app/topicsContext.ts'
import { feedUrl } from '../../routes/paths.ts'
import { useSubmit } from './useSubmit.ts'
import './SubmitPage.css'

function bodyFrom(form: FormData): SubmitItemBody {
  const text = (name: string) => String(form.get(name) ?? '').trim()
  return {
    url: text('url'),
    title: text('title'),
    topic: text('topic'),
    tags: text('tags')
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean),
  }
}

function SubmitPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const topicsState = useTopics()
  const { state, submit } = useSubmit((body) => navigate(feedUrl({ topic: body.topic })))

  if (topicsState.status === 'loading') return <LoadingState label="Loading topics" />
  if (topicsState.status === 'error') {
    return <ErrorState title="Could not load topics." error={topicsState.error} />
  }
  const topics = topicsState.topics

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
        <label className="field-label" htmlFor="topic">
          topic
        </label>
        <select className="input" id="topic" name="topic" required defaultValue={params.get('topic') ?? ''}>
          <option value="" disabled>
            choose a topic
          </option>
          {topics.map((topic) => (
            <option key={topic.slug} value={topic.slug}>
              {topic.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label className="field-label" htmlFor="tags">
          tags
        </label>
        <input className="input" id="tags" name="tags" aria-describedby="tags-help" defaultValue={params.get('tags') ?? ''} />
        <p className="field-help" id="tags-help">
          Comma-separated, up to 5, from the topic's tag list.
        </p>
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
