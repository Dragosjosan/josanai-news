import { useState } from 'react'
import { useNavigate } from 'react-router'
import { deleteItem } from '../../../api/items.ts'
import { paths } from '../../../routes/paths.ts'

function DeleteItemButton({ id }: { id: number }) {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  async function remove() {
    if (!window.confirm('Delete this story?')) return
    setError(null)
    try {
      await deleteItem(id)
      navigate(paths.home)
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Could not delete this story.')
    }
  }

  return (
    <>
      <span className="item-article-separator" aria-hidden="true">|</span>
      <button className="item-article-delete" type="button" onClick={() => void remove()}>delete</button>
      {error && <span role="alert">{error}</span>}
    </>
  )
}

export default DeleteItemButton
