import { useState } from 'react'
import { voteItem } from '../../api/items.ts'
import type { FeedItem } from '../../api/types.ts'

export function useVote(item: Pick<FeedItem, 'id' | 'score' | 'viewer_vote'>) {
  const [score, setScore] = useState(item.score)
  const [voted, setVoted] = useState(item.viewer_vote === 'up')
  const [pending, setPending] = useState(false)

  function toggle() {
    if (pending) return
    setPending(true)
    voteItem(item.id, voted ? 'none' : 'up')
      .then((result) => {
        setScore(result.score)
        setVoted(result.viewer_vote === 'up')
      })
      .catch(() => undefined)
      .finally(() => setPending(false))
  }

  return { score, voted, pending, toggle }
}
