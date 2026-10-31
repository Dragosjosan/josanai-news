import { useParams } from 'react-router'
import type { ItemDetail } from '../../api/types.ts'
import { ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import Comments from '../comments/Comments.tsx'
import { useComments } from '../comments/useComments.ts'
import ItemArticle from './components/ItemArticle.tsx'
import { useItem } from './useItem.ts'

function ItemPage() {
  const { id } = useParams()
  const state = useItem(Number(id))

  if (state.status === 'loading') return <LoadingState label="Loading story" />
  if (state.status === 'error') return <ErrorState title="Could not load this story." error={state.error} />

  return <ItemDiscussion key={state.item.id} item={state.item} />
}

function ItemDiscussion({ item }: { item: ItemDetail }) {
  const discussion = useComments(item.id)
  const count = discussion.state.status === 'ready'
    ? discussion.state.comments.filter((comment) => !comment.deleted).length
    : item.comment_count

  return (
    <>
      <ItemArticle item={{ ...item, comment_count: count }} />
      <Comments discussion={discussion} />
    </>
  )
}

export default ItemPage
