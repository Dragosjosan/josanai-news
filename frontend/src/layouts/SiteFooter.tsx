import './SiteFooter.css'

function SiteFooter() {
  return (
    <footer className="site-footer">
      <span className="site-footer-note">
        Powered by <a href="https://josan.ai">josan.ai</a>.
      </span>
      <a className="site-footer-note" href="/agents">for agents</a>
    </footer>
  )
}

export default SiteFooter
