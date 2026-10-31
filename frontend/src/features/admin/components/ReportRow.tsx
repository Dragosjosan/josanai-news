import { Link } from 'react-router'
import type { useReports } from '../useReports.ts'
import type { ReviewReport } from '../../../api/types.ts'
import { timeAgo } from '../../../lib/format.ts'
import { itemUrl } from '../../../routes/paths.ts'

type Props = {
  report: ReviewReport
  reports: ReturnType<typeof useReports>
}

function ReportRow({ report, reports }: Props) {
  const { item, comment } = report
  const target = comment ? `${itemUrl(item.id)}#comment-${comment.id}` : itemUrl(item.id)
  const author = comment ? comment.author : item.username

  return (
    <li className="report-row">
      <Link className="report-title" to={target}>{item.title}</Link>
      <div className="report-meta">
        <span>{comment ? 'comment' : 'story'}</span>
        {author && <span>by {author}</span>}
        <span>
          {report.harm_probability === null
            ? 'not checked, Jev was down'
            : `harm ${Math.round(report.harm_probability * 100)}%`}
        </span>
        <span>{timeAgo(report.created_at)}</span>
      </div>
      {comment && <p className="report-comment">{comment.text}</p>}
      <div className="report-actions">
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
            onClick={() => void reports.removeAll(report, 'submitter')}
          >delete all from submitter</button>
        )}
        {!comment && item.username && (
          <button
            className="btn btn-ghost btn-compact"
            type="button"
            disabled={reports.pending}
            onClick={() => void reports.removeAll(report, 'account')}
          >delete all from account</button>
        )}
      </div>
    </li>
  )
}

export default ReportRow
