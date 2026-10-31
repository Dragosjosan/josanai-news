import { Link } from 'react-router'
import { logout } from '../api/auth.ts'
import { useAuth } from '../app/authContext.ts'
import { paths } from '../routes/paths.ts'
import './AccountLinks.css'

function AccountLinks() {
  const { account, setAccount } = useAuth()

  if (!account) return <Link to={paths.login}>login</Link>

  return (
    <>
      <span>{account.username}</span>
      <span aria-hidden="true">|</span>
      {account.role === 'admin' && (
        <>
          <Link to={paths.admin}>admin</Link>
          <span aria-hidden="true">|</span>
        </>
      )}
      <button
        type="button"
        className="account-logout"
        onClick={() => {
          void logout().then(() => setAccount(null))
        }}
      >
        logout
      </button>
    </>
  )
}

export default AccountLinks
