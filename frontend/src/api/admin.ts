import { deleteJson, getJson, postJson, putJson } from './client.ts'
import type { Account, BulkDeleteBy, BulkDeleteResult, ReportList } from './types.ts'

export function fetchReports(signal?: AbortSignal): Promise<ReportList> {
  return getJson<ReportList>('/admin/reports', {}, signal)
}

export function hideReport(id: number): Promise<void> {
  return postJson<void>(`/admin/reports/${id}/hide`)
}

export function bulkDelete(itemId: number, by: BulkDeleteBy, dryRun: boolean): Promise<BulkDeleteResult> {
  return postJson<BulkDeleteResult>('/admin/items/bulk-delete', { item_id: itemId, by, dry_run: dryRun })
}

export function makeAdmin(username: string): Promise<Account> {
  return putJson<Account>(`/admin/accounts/${encodeURIComponent(username)}/admin`, undefined)
}

export function deleteAccount(username: string): Promise<void> {
  return deleteJson(`/admin/accounts/${encodeURIComponent(username)}`)
}
