import type { ReactNode } from 'react'
import './LinkSection.css'

function LinkSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="link-section">
      <h2 className="link-section-title">{title}</h2>
      <ul className="link-section-list">{children}</ul>
    </section>
  )
}

export default LinkSection
