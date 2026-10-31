export const paths = {
  home: '/',
  newest: '/newest',
  past: '/front',
  search: '/search',
  submit: '/submit',
  login: '/login',
  admin: '/admin',
  adminReports: '/admin/reports',
  adminAccounts: '/admin/accounts',
  item: '/item/:id',
} as const

export function itemUrl(id: number): string {
  return `/item/${id}`
}

export function pastUrl(day: string): string {
  return `${paths.past}?day=${day}`
}

export function searchUrl(q: string, page = 1): string {
  const params = new URLSearchParams({ q })
  if (page > 1) params.set('page', String(page))
  return `${paths.search}?${params.toString()}`
}
