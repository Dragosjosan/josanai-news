import { useLocation } from 'react-router'
import type { ItemDetail } from '../../../api/types.ts'
import { useAuth } from '../../../app/authContext.ts'
import DisclosureToggle from '../../../components/Disclosure/DisclosureToggle.tsx'
import { useDisclosure } from '../../../components/Disclosure/useDisclosure.ts'
import ExternalLink from '../../../components/ExternalLink/ExternalLink.tsx'
import VoteArrow from '../../../components/VoteArrow/VoteArrow.tsx'
import { useVote } from '../../../components/VoteArrow/useVote.ts'
import { pluralize, timeAgo } from '../../../lib/format.ts'
import DeleteItemButton from './DeleteItemButton.tsx'
import './ItemArticle.css'

function ItemArticle({ item }: { item: ItemDetail }) {
  const { account } = useAuth()
  const vote = useVote(item)
  const { hash } = useLocation()
  const summary = useDisclosure(hash === '#summary')

  return (
    <article className="item-article">
      <VoteArrow title={item.title} voted={vote.voted} pending={vote.pending} onToggle={vote.toggle} />

      <div className="item-article-body">
        <div className="item-article-headline">
          <ExternalLink className="item-article-title" href={item.url}>
            {item.title}
          </ExternalLink>
          <span className="item-article-domain">({item.domain})</span>
        </div>

        <div className="item-article-meta">
          <span className="item-article-score">{pluralize(vote.score, 'point')}</span>
          {item.username && (
            <span>
              by {item.username}
              {item.label && ` (${item.label})`}
            </span>
          )}
          <time dateTime={item.created_at} title={new Date(item.created_at).toLocaleString()}>
            {timeAgo(item.created_at)}
          </time>
          {item.summary && (
            <>
              <span className="item-article-separator" aria-hidden="true">|</span>
              <DisclosureToggle
                label="summary"
                expandedLabel="hide summary"
                expanded={summary.expanded}
                contentId={summary.contentId}
                onToggle={summary.toggle}
              />
            </>
          )}
          <span className="item-article-separator" aria-hidden="true">|</span>
          <span>{item.comment_count === 0 ? 'discuss' : pluralize(item.comment_count, 'comment')}</span>
          {account?.role === 'admin' && <DeleteItemButton id={item.id} />}
        </div>

        {item.summary && (
          <p className="item-article-summary" id={summary.contentId} hidden={!summary.expanded}>
            {item.summary}
          </p>
        )}
      </div>
    </article>
  )
}

export default ItemArticle
