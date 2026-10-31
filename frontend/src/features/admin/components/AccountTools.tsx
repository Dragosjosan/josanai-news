import { useState } from 'react'
import { deleteAccount, makeAdmin } from '../../../api/admin.ts'

function AccountTools() {
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
    <section className="admin-section" aria-label="Accounts">
      <h2 className="admin-heading">accounts</h2>
      <div className="admin-account-form">
        <label className="field-label" htmlFor="admin-username">username</label>
        <input
          className="input"
          id="admin-username"
          maxLength={32}
          value={username}
          onChange={(event) => setUsername(event.currentTarget.value)}
        />
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
    </section>
  )
}

export default AccountTools
