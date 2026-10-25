import { useId, useState } from 'react'

export function useDisclosure(initialExpanded = false) {
  const [expanded, setExpanded] = useState(initialExpanded)
  const contentId = useId()

  function toggle() {
    setExpanded((current) => !current)
  }

  return { expanded, contentId, toggle }
}
