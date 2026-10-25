import { NavLink } from 'react-router'
import { paths } from '../routes/paths.ts'
import AccountLinks from './AccountLinks.tsx'
import './SiteHeader.css'

function SiteHeader() {
  return (
    <header className="site-header">
      <NavLink to={paths.home} className="site-brand">
        news.josan.ai
      </NavLink>

      <nav className="site-nav" aria-label="Main">
        <NavLink to={paths.newest} className="site-nav-link">
          new
        </NavLink>
        <NavLink to={paths.past} className="site-nav-link">
          past
        </NavLink>
        <NavLink to={paths.search} className="site-nav-link">
          search
        </NavLink>
      </nav>

      <div className="site-actions">
        <NavLink to={paths.submit}>submit</NavLink>
        <span aria-hidden="true">|</span>
        <AccountLinks />
      </div>
    </header>
  )
}

export default SiteHeader
