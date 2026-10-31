import { useAuth } from '../../app/authContext.ts'
import { EmptyState, ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import AccountTools from './components/AccountTools.tsx'
import ReportRow from './components/ReportRow.tsx'
import { useReports } from './useReports.ts'
import './AdminPage.css'

function ReportList() {
  const reports = useReports()
  const { state } = reports

  if (state.status === 'loading') return <LoadingState label="Loading reports" />
  if (state.status === 'error') return <ErrorState title="Could not load reports." error={state.error} />
  if (state.reports.length === 0) return <EmptyState title="No open reports." />

  return (
    <>
      {reports.actionError && <p className="admin-message" role="alert">{reports.actionError}</p>}
      <ol className="report-list">
        {state.reports.map((report) => (
          <ReportRow key={report.id} report={report} reports={reports} />
        ))}
      </ol>
    </>
  )
}

function AdminPage() {
  const { account } = useAuth()

  if (account?.role !== 'admin') return <EmptyState title="Admins only." copy="Log in with an admin account." />

  return (
    <div className="admin-page">
      <section className="admin-section" aria-label="Reports">
        <h2 className="admin-heading">reports</h2>
        <ReportList />
      </section>
      <AccountTools />
    </div>
  )
}

export default AdminPage
