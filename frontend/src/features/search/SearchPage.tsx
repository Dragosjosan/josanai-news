import type { FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import FeedView from '../feed/components/FeedView.tsx'
import { searchUrl } from '../../routes/paths.ts'
import { useSearch } from './useSearch.ts'
import './SearchPage.css'

const PAGE_SIZE = 70

function SearchResults({ q, page }: { q: string; page: number }) {
  const { feed, hasMore } = useSearch(q, page)

  return (
    <>
      <FeedView state={feed} start={(page - 1) * PAGE_SIZE + 1} />
      {hasMore && (
        <Link className="search-more" to={searchUrl(q, page + 1)}>
          More
        </Link>
      )}
    </>
  )
}

function SearchPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const q = params.get('q')?.trim() ?? ''
  const page = Math.max(Number(params.get('page')) || 1, 1)

  return (
    <>
      <form
        className="search-form"
        role="search"
        onSubmit={(event: FormEvent<HTMLFormElement>) => {
          event.preventDefault()
          const value = String(new FormData(event.currentTarget).get('q') ?? '').trim()
          navigate(searchUrl(value))
        }}
      >
        <input
          key={q}
          className="input"
          name="q"
          type="search"
          aria-label="Search stories"
          maxLength={200}
          defaultValue={q}
        />
        <button type="submit" className="btn btn-primary">
          search
        </button>
      </form>
      {q && <SearchResults q={q} page={page} />}
    </>
  )
}

export default SearchPage
