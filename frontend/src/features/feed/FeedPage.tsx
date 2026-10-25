import FeedView from './components/FeedView.tsx'
import { useFeed } from './useFeed.ts'

function FeedPage({ sort }: { sort: 'top' | 'new' }) {
  return <FeedView state={useFeed(sort)} />
}

export default FeedPage
