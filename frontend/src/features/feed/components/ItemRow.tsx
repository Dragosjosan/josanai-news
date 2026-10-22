import { Link } from 'react-router'
import type { FeedItem } from '../../../api/types.ts'
import ExternalLink from '../../../components/ExternalLink/ExternalLink.tsx'
import VoteArrow from '../../../components/VoteArrow/VoteArrow.tsx'
import { useVote } from '../../../components/VoteArrow/useVote.ts'
import { pluralize, timeAgo } from '../../../lib/format.ts'
import { itemUrl } from '../../../routes/paths.ts'
import './ItemRow.css'

type ItemRowProps = {
  item: FeedItem
  rank: number
}

function ItemRow({ item, rank }: ItemRowProps) {
  const vote = useVote(item)

  return (
    <li className="item-row">
      <span className="item-rank">{rank}.</span>

      <VoteArrow title={item.title} voted={vote.voted} pending={vote.pending} onToggle={vote.toggle} />

      <div className="item-body">
        <div className="item-headline">
          <ExternalLink className="item-title" href={item.url}>
            {item.title}
          </ExternalLink>
          <span className="item-domain"> ({item.domain})</span>
        </div>

        <div className="item-meta">
          <span>
            {pluralize(vote.score, 'point')}
            {item.username && ` by ${item.username}`}
            {item.username && item.label && ` (${item.label})`}
          </span>
          <time dateTime={item.created_at} title={new Date(item.created_at).toLocaleString()}>
            {timeAgo(item.created_at)}
          </time>
          <span aria-hidden="true">|</span>
          <Link className="item-comments" to={itemUrl(item.id)}>
            {item.comment_count === 0 ? 'discuss' : pluralize(item.comment_count, 'comment')}
          </Link>
        </div>
      </div>
    </li>
  )
}

export default ItemRow
