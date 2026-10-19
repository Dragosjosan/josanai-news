import type { FeedItem } from '../../../api/types.ts'
import { pluralize, timeAgo } from '../../../lib/format.ts'
import './ItemRow.css'

type ItemRowProps = {
  item: FeedItem
  rank: number
}

function ItemRow({ item, rank }: ItemRowProps) {
  return (
    <li className="item-row">
      <span className="item-rank">{rank}.</span>

      <button type="button" className="item-vote" aria-label={`Upvote ${item.title}`} disabled>
        ▲
      </button>

      <div className="item-body">
        <div className="item-headline">
          <a className="item-title" href={item.url} rel="noopener noreferrer">
            {item.title}
          </a>
          <span className="item-domain"> ({item.domain})</span>
        </div>

        <div className="item-meta">
          <span>
            {pluralize(item.score, 'point')}
            {item.publisher && ` by ${item.publisher}`}
          </span>
          <time dateTime={item.created_at} title={new Date(item.created_at).toLocaleString()}>
            {timeAgo(item.created_at)}
          </time>
          <span aria-hidden="true">|</span>
          <span>{item.comment_count === 0 ? 'discuss' : pluralize(item.comment_count, 'comment')}</span>
        </div>
      </div>
    </li>
  )
}

export default ItemRow
