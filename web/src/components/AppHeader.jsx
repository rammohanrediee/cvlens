import { BrandMark, Icon } from './Icon.jsx'

export default function AppHeader({ onNavigate, onJobMatch, serviceStatus }) {
  return (
    <header className="product-header">
      <a className="skip-link" href="#app-content">Skip to content</a>
      <button className="brand" type="button" onClick={() => onNavigate('analyze')} aria-label="ResumeAI home"><BrandMark /><span>ResumeAI</span></button>
      <nav aria-label="Application">
        <button type="button" className="nav-current" aria-current="page" onClick={() => onNavigate('analyze')}>Analyze</button>
        <button type="button" onClick={onJobMatch}>Job match</button>
      </nav>
      <span className={serviceStatus === 'offline' ? 'service-note' : 'session-badge'}><Icon name={serviceStatus === 'offline' ? 'alert' : 'shield'} size={15} />{serviceStatus === 'offline' ? 'Offline' : 'This session'}</span>
    </header>
  )
}
