import { useEffect, useState } from 'react'
import { bulkDelete, fetchReports, hideReport } from '../../api/admin.ts'
import { deleteComment } from '../../api/comments.ts'
import { deleteItem } from '../../api/items.ts'
import type { ReviewReport } from '../../api/types.ts'
import { pluralize } from '../../lib/format.ts'

type ReportsState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; reports: ReviewReport[] }

export function useReports() {
  const [state, setState] = useState<ReportsState>({ status: 'loading' })
  const [pending, setPending] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    fetchReports(controller.signal)
      .then((list) => setState({ status: 'ready', reports: list.reports }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ status: 'error', error })
      })
    return () => controller.abort()
  }, [revision])

  async function run(action: () => Promise<unknown>) {
    setPending(true)
    setActionError(null)
    try {
      await action()
      setRevision((current) => current + 1)
    } catch (failure) {
      setActionError(failure instanceof Error ? failure.message : 'The action failed.')
    } finally {
      setPending(false)
    }
  }

  function hide(report: ReviewReport) {
    return run(() => hideReport(report.id))
  }

  function remove(report: ReviewReport) {
    return run(() => (report.comment ? deleteComment(report.comment.id) : deleteItem(report.item.id)))
  }

  function removeAll(report: ReviewReport) {
    return run(async () => {
      const { deleted } = await bulkDelete(report.item.id, true)
      if (window.confirm(`Delete ${pluralize(deleted, 'story', 'stories')} from this submitter?`)) {
        await bulkDelete(report.item.id, false)
      }
    })
  }

  return { state, pending, actionError, hide, remove, removeAll }
}
