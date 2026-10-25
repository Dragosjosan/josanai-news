import type { FeedItem } from '../../../api/types.ts'
import ItemRow from './ItemRow.tsx'
import './ItemList.css'

function ItemList({ items, start = 1 }: { items: FeedItem[]; start?: number }) {
  return (
    <ol className="item-list" start={start}>
      {items.map((item, index) => (
        <ItemRow key={item.id} item={item} rank={start + index} />
      ))}
    </ol>
  )
}

export default ItemList
