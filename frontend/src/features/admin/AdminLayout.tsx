import { NavLink, Outlet } from 'react-router'
import { useAuth } from '../../app/authContext.ts'
import { EmptyState } from '../../components/AsyncState/AsyncState.tsx'
import { paths } from '../../routes/paths.ts'
import './AdminLayout.css'

function AdminLayout() {
  const { account } = useAuth()

  if (account?.role !== 'admin') return <EmptyState title="Admins only." copy="Log in with an admin account." />

  return (
    <div className="admin-layout">
      <nav className="admin-nav" aria-label="Admin">
        <NavLink className="admin-nav-link" to={paths.adminReports}>Reports</NavLink>
        <NavLink className="admin-nav-link" to={paths.adminAccounts}>Accounts</NavLink>
      </nav>
      <div className="admin-panel">
        <Outlet />
      </div>
    </div>
  )
}

export default AdminLayout
