import './DisclosureToggle.css'

type DisclosureToggleProps = {
  label: string
  expandedLabel: string
  expanded: boolean
  contentId: string
  onToggle: () => void
}

function DisclosureToggle({ label, expandedLabel, expanded, contentId, onToggle }: DisclosureToggleProps) {
  return (
    <button
      type="button"
      className="disclosure-toggle"
      aria-expanded={expanded}
      aria-controls={contentId}
      onClick={onToggle}
    >
      {expanded ? expandedLabel : label}
    </button>
  )
}

export default DisclosureToggle
