import { createBrowserRouter } from 'react-router'
import AppLayout from '../layouts/AppLayout.tsx'
import FeedPage from '../features/feed/FeedPage.tsx'
import ItemPage from '../features/item/ItemPage.tsx'
import NotFoundPage from '../features/not-found/NotFoundPage.tsx'
import SubmitPage from '../features/submit/SubmitPage.tsx'
import { paths } from './paths.ts'

export const router = createBrowserRouter([
  {
    path: paths.home,
    element: <AppLayout />,
    children: [
      { index: true, element: <FeedPage /> },
      { path: paths.submit, element: <SubmitPage /> },
      { path: paths.item, element: <ItemPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
