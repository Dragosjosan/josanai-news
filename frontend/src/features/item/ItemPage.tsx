import { useParams } from 'react-router'
import { ErrorState, LoadingState } from '../../components/AsyncState/AsyncState.tsx'
import ItemArticle from './components/ItemArticle.tsx'
import { useItem } from './useItem.ts'

function ItemPage() {
  const { id } = useParams()
  const state = useItem(Number(id))

  if (state.status === 'loading') return <LoadingState label="Loading story" />
  if (state.status === 'error') return <ErrorState title="Could not load this story." error={state.error} />

  return <ItemArticle key={state.item.id} item={state.item} />
}

export default ItemPage
