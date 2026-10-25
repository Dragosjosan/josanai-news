import { Link, useSearchParams } from 'react-router'
import FeedView from '../feed/components/FeedView.tsx'
import { useFeed } from '../feed/useFeed.ts'
import { addDays, isDay, todayUtc } from '../../lib/day.ts'
import { pastUrl } from '../../routes/paths.ts'
import './PastPage.css'

function PastPage() {
  const [params] = useSearchParams()
  const requested = params.get('day')
  const day = isDay(requested) ? requested : addDays(todayUtc(), -1)
  const state = useFeed('top', day)
  const next = addDays(day, 1)

  return (
    <>
      <nav className="past-nav" aria-label="Days">
        <span className="past-day">Stories from {day}</span>
        <Link to={pastUrl(addDays(day, -1))}>go back a day</Link>
        {next <= todayUtc() && <Link to={pastUrl(next)}>go forward a day</Link>}
      </nav>
      <FeedView state={state} />
    </>
  )
}

export default PastPage
