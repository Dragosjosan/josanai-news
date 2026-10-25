import { ErrorState, LoadingState } from '../../../components/AsyncState/AsyncState.tsx'
import type { FeedState } from '../useFeed.ts'
import ItemList from './ItemList.tsx'
import './FeedView.css'

function FeedView({ state, start = 1 }: { state: FeedState; start?: number }) {
  if (state.status === 'loading') return <LoadingState label="Loading stories" />
  if (state.status === 'error') return <ErrorState title="Could not load stories." error={state.error} />
  if (state.items.length === 0) return <p className="feed-empty">No stories.</p>
  return <ItemList items={state.items} start={start} />
}

export default FeedView
