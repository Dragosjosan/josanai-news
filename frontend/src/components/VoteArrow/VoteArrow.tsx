import './VoteArrow.css'

type VoteArrowProps = {
  title: string
  voted: boolean
  pending: boolean
  onToggle: () => void
}

function VoteArrow({ title, voted, pending, onToggle }: VoteArrowProps) {
  return (
    <button
      type="button"
      className="vote-arrow"
      aria-label={voted ? `Remove upvote from ${title}` : `Upvote ${title}`}
      aria-pressed={voted}
      disabled={pending}
      onClick={onToggle}
    >
      ▲
    </button>
  )
}

export default VoteArrow
