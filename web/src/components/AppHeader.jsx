import { BrandMark, Icon } from './Icon.jsx'

export default function AppHeader({ onNavigate, onJobMatch, onThemeChange, theme }) {
  return (
    <header className="product-header">
      <a className="skip-link" href="#app-content">Skip to content</a>
      <button className="brand" type="button" onClick={() => onNavigate('analyze')} aria-label="cvLens home"><BrandMark /><span>cvLens</span></button>
      <nav aria-label="Application">
        <button type="button" className="nav-current" aria-current="page" onClick={() => onNavigate('analyze')}>Analyze</button>
        <button type="button" onClick={onJobMatch}>Job match</button>
      </nav>
      <button className="theme-toggle" type="button" onClick={onThemeChange} aria-label={theme === 'dark' ? 'Use light theme' : 'Use dark theme'} title={theme === 'dark' ? 'Use light theme' : 'Use dark theme'}><Icon name={theme === 'dark' ? 'sun' : 'moon'} size={18} /></button>
    </header>
  )
}
