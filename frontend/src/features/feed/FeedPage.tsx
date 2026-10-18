import { useSearchParams } from 'react-router'
import { ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import ItemList from './components/ItemList.tsx'
import TagFilter from './components/TagFilter.tsx'
import { useFeed } from './useFeed.ts'
import './FeedPage.css'

function FeedPage() {
  const [searchParams] = useSearchParams()
  const topic = searchParams.get('topic') ?? undefined
  const tag = searchParams.get('tag') ?? undefined

  const feed = useFeed({ topic, tag })

  return (
    <div className="feed-page">
      <TagFilter topic={topic} tag={tag} />

      {feed.status === 'loading' && <LoadingState label="Loading stories" />}
      {feed.status === 'idle' && feed.items.length === 0 && <p className="feed-empty">No posts.</p>}
      {feed.items.length > 0 && <ItemList items={feed.items} />}

      {feed.status === 'error' && feed.error && (
        <ErrorState title="Could not load stories." error={feed.error} />
      )}
    </div>
  )
}

export default FeedPage
