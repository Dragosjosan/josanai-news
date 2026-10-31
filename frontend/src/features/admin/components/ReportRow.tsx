import { Link } from 'react-router'
import type { ReviewReport } from '../../../api/types.ts'
import { timeAgo } from '../../../lib/format.ts'
import { itemUrl } from '../../../routes/paths.ts'
import type { useReports } from '../useReports.ts'

type Props = {
  report: ReviewReport
  reports: ReturnType<typeof useReports>
}

function ReportRow({ report, reports }: Props) {
  const { item, comment } = report
  const target = comment ? `${itemUrl(item.id)}#comment-${comment.id}` : itemUrl(item.id)
  const author = comment ? comment.author : item.username

  return (
    <tr>
      <td className="report-target">
        <Link className="report-title" to={target}>{item.title}</Link>
        {comment && <p className="report-comment">{comment.text}</p>}
      </td>
      <td className="report-cell">
        {report.harm_probability === null
          ? <span className="badge badge-neutral">not checked</span>
          : <span className="badge badge-warning">harm {Math.round(report.harm_probability * 100)}%</span>}
      </td>
      <td className="report-cell">{author ?? 'anonymous'}</td>
      <td className="report-cell">{timeAgo(report.created_at)}</td>
      <td>
        <div className="admin-actions">
          <button
            className="btn btn-ghost btn-compact"
            type="button"
            disabled={reports.pending}
            onClick={() => void reports.hide(report)}
          >hide</button>
          <button
            className="btn btn-danger btn-compact"
            type="button"
            disabled={reports.pending}
            onClick={() => void reports.remove(report)}
          >delete</button>
          {!comment && (
            <button
              className="btn btn-ghost btn-compact"
              type="button"
              disabled={reports.pending}
              onClick={() => void reports.removeAll(report)}
            >delete all from submitter</button>
          )}
        </div>
      </td>
    </tr>
  )
}

export default ReportRow
