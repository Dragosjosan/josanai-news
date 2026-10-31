import { createBrowserRouter, Navigate } from 'react-router'
import AppLayout from '../layouts/AppLayout.tsx'
import AccountsPage from '../features/admin/AccountsPage.tsx'
import AdminLayout from '../features/admin/AdminLayout.tsx'
import ReportsPage from '../features/admin/ReportsPage.tsx'
import LoginPage from '../features/auth/LoginPage.tsx'
import FeedPage from '../features/feed/FeedPage.tsx'
import ItemPage from '../features/item/ItemPage.tsx'
import NotFoundPage from '../features/not-found/NotFoundPage.tsx'
import PastPage from '../features/past/PastPage.tsx'
import SearchPage from '../features/search/SearchPage.tsx'
import SubmitPage from '../features/submit/SubmitPage.tsx'
import { paths } from './paths.ts'

export const router = createBrowserRouter([
  {
    path: paths.home,
    element: <AppLayout />,
    children: [
      { index: true, element: <FeedPage sort="top" /> },
      { path: paths.newest, element: <FeedPage key="new" sort="new" /> },
      { path: paths.past, element: <PastPage /> },
      { path: paths.search, element: <SearchPage /> },
      { path: paths.submit, element: <SubmitPage /> },
      { path: paths.login, element: <LoginPage /> },
      {
        path: paths.admin,
        element: <AdminLayout />,
        children: [
          { index: true, element: <Navigate to={paths.adminReports} replace /> },
          { path: paths.adminReports, element: <ReportsPage /> },
          { path: paths.adminAccounts, element: <AccountsPage /> },
        ],
      },
      { path: paths.item, element: <ItemPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
