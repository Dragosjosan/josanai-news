import type { ReactNode } from 'react'
import { isWebUrl } from '../../lib/url.ts'

type ExternalLinkProps = {
  href: string
  className?: string
  children: ReactNode
}

function ExternalLink({ href, className, children }: ExternalLinkProps) {
  if (!isWebUrl(href)) return <span className={className}>{children}</span>

  return (
    <a className={className} href={href} rel="noopener noreferrer nofollow ugc">
      {children}
    </a>
  )
}

export default ExternalLink
