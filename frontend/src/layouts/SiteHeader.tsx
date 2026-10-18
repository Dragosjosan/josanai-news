import { Link, useSearchParams } from 'react-router'
import { useTopics } from '../app/topicsContext.ts'
import { feedUrl, paths } from '../routes/paths.ts'
import './SiteHeader.css'

function SiteHeader() {
  const topicsState = useTopics()
  const [searchParams] = useSearchParams()
  const activeTopic = searchParams.get('topic')
  const topics = topicsState.status === 'ready' ? topicsState.topics : []

  return (
    <header className="site-header">
      <Link to={paths.home} className="site-brand">
        news.josan.ai
      </Link>

      <nav className="site-nav" aria-label="Topics">
        {topics.map((topic) => (
          <Link
            key={topic.slug}
            to={feedUrl({ topic: topic.slug })}
            className="site-nav-link"
            aria-current={activeTopic === topic.slug ? 'page' : undefined}
          >
            {topic.slug}
          </Link>
        ))}
      </nav>
    </header>
  )
}

export default SiteHeader
