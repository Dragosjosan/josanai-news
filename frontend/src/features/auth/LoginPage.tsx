import type { FormEvent } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../../app/authContext.ts'
import { paths } from '../../routes/paths.ts'
import { useLogin } from './useLogin.ts'
import './LoginPage.css'

function LoginPage() {
  const navigate = useNavigate()
  const { setAccount } = useAuth()
  const { state, submit } = useLogin((account) => {
    setAccount(account)
    navigate(paths.home)
  })

  return (
    <form
      className="login-form stack"
      onSubmit={(event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const form = new FormData(event.currentTarget)
        void submit({ username: String(form.get('username') ?? ''), password: String(form.get('password') ?? '') })
      }}
    >
      <div className="field">
        <label className="field-label" htmlFor="username">
          username
        </label>
        <input className="input" id="username" name="username" autoComplete="username" required maxLength={32} />
      </div>

      <div className="field">
        <label className="field-label" htmlFor="password">
          password
        </label>
        <input
          className="input"
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          maxLength={128}
        />
      </div>

      {state.status === 'error' && (
        <div className="alert alert-danger" role="alert">
          <div className="alert-content">
            <p>{state.message}</p>
          </div>
        </div>
      )}

      <div>
        <button type="submit" className="btn btn-primary" disabled={state.status === 'sending'}>
          login
        </button>
      </div>
    </form>
  )
}

export default LoginPage
