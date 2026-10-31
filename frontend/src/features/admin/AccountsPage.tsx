import { useState } from 'react'
import { deleteAccount, makeAdmin } from '../../api/admin.ts'

function AccountsPage() {
  const [username, setUsername] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const name = username.trim()

  async function run(action: () => Promise<unknown>, done: string) {
    setBusy(true)
    setMessage(null)
    try {
      await action()
      setMessage(done)
      setUsername('')
    } catch (failure) {
      setMessage(failure instanceof Error ? failure.message : 'The action failed.')
    } finally {
      setBusy(false)
    }
  }

  function remove() {
    if (window.confirm(`Delete the account ${name}? Its posts stay on the site.`)) {
      void run(() => deleteAccount(name), `Deleted ${name}.`)
    }
  }

  return (
    <>
      <header className="admin-panel-header">
        <h1 className="admin-title">Accounts</h1>
      </header>
      <div className="card card-compact admin-account-card">
        <div className="field">
          <label className="field-label" htmlFor="admin-username">username</label>
          <input
            className="input"
            id="admin-username"
            maxLength={32}
            value={username}
            onChange={(event) => setUsername(event.currentTarget.value)}
          />
        </div>
        <div className="admin-actions">
          <button
            className="btn btn-ghost btn-compact"
            type="button"
            disabled={busy || !name}
            onClick={() => void run(() => makeAdmin(name), `${name} is now an admin.`)}
          >make admin</button>
          <button
            className="btn btn-danger btn-compact"
            type="button"
            disabled={busy || !name}
            onClick={remove}
          >delete account</button>
        </div>
        {message && <p className="admin-message" role="status">{message}</p>}
      </div>
    </>
  )
}

export default AccountsPage
