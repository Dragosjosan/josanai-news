import { Link } from 'react-router'
import type { ItemRef } from '../../../api/types.ts'
import { timeAgo } from '../../../lib/format.ts'
import { itemUrl } from '../../../routes/paths.ts'
import LinkSection from './LinkSection.tsx'

function ConnectionList({ title, items }: { title: string; items: ItemRef[] }) {
  return (
    <LinkSection title={title}>
      {items.map((ref) => (
        <li key={ref.id}>
          <Link className="link-section-link" to={itemUrl(ref.id)}>
            {ref.title}
          </Link>
          <span className="link-section-note">
            ({ref.domain}) {timeAgo(ref.created_at)}
          </span>
        </li>
      ))}
    </LinkSection>
  )
}

export default ConnectionList
