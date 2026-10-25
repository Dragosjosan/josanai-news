import type { ItemDetail } from '../../../api/types.ts'
import ExternalLink from '../../../components/ExternalLink/ExternalLink.tsx'
import VoteArrow from '../../../components/VoteArrow/VoteArrow.tsx'
import { useVote } from '../../../components/VoteArrow/useVote.ts'
import { pluralize, timeAgo } from '../../../lib/format.ts'
import ConnectionList from './ConnectionList.tsx'
import LinkSection from './LinkSection.tsx'
import './ItemArticle.css'

function ItemArticle({ item }: { item: ItemDetail }) {
  const vote = useVote(item)

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
          <span className="item-article-separator" aria-hidden="true">|</span>
          <span>{item.comment_count === 0 ? 'discuss' : pluralize(item.comment_count, 'comment')}</span>
        </div>

        {item.summary && <p className="item-article-summary">{item.summary}</p>}

        {item.corroborating.length > 0 && (
          <LinkSection title="Verified against">
            {item.corroborating.map((link) => (
              <li key={link.url}>
                <ExternalLink className="link-section-link" href={link.url}>
                  {link.domain}
                </ExternalLink>
              </li>
            ))}
          </LinkSection>
        )}

        {item.earlier.length > 0 && <ConnectionList title="Updates" items={item.earlier} />}
        {item.later.length > 0 && <ConnectionList title="Updated by" items={item.later} />}
      </div>
    </article>
  )
}

export default ItemArticle
