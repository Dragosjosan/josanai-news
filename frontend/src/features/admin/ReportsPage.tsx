import { EmptyState, ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import ReportRow from './components/ReportRow.tsx'
import { useReports } from './useReports.ts'

function ReportsPage() {
  const reports = useReports()
  const { state } = reports

  return (
    <>
      <header className="admin-panel-header">
        <h1 className="admin-title">Reports</h1>
        {state.status === 'ready' && <span className="admin-count">{state.reports.length} open</span>}
      </header>
      {state.status === 'loading' && <LoadingState label="Loading reports" />}
      {state.status === 'error' && <ErrorState title="Could not load reports." error={state.error} />}
      {state.status === 'ready' && state.reports.length === 0 && <EmptyState title="No open reports." />}
      {state.status === 'ready' && state.reports.length > 0 && (
        <>
          {reports.actionError && <p className="admin-message" role="alert">{reports.actionError}</p>}
          <div className="table-wrap">
            <table className="table table-compact table-hover">
              <thead>
                <tr>
                  <th scope="col">Reported</th>
                  <th scope="col">Jev</th>
                  <th scope="col">By</th>
                  <th scope="col">When</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {state.reports.map((report) => (
                  <ReportRow key={report.id} report={report} reports={reports} />
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}

export default ReportsPage
