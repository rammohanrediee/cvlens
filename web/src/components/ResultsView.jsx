import { useEffect, useRef, useState } from 'react'
import { Icon } from './Icon.jsx'

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'ats', label: 'Checks' },
  { id: 'suggestions', label: 'Suggestions' },
  { id: 'keywords', label: 'Job match' },
]

function scoreValue(value) {
  return value == null || !Number.isFinite(Number(value)) ? null : Math.round(Math.max(0, Math.min(100, Number(value))))
}

function Breakdown({ sections }) {
  return (
    <section className="breakdown" aria-labelledby="breakdown-title">
      <h3 id="breakdown-title">Section breakdown</h3>
      <dl className="score-list">{sections.map((section) => (
        <div className="score-row" key={section.category}><dt>{section.category}</dt><dd>{scoreValue(section.percent) ?? '—'}<small> / 100</small></dd></div>
      ))}</dl>
    </section>
  )
}

function EmptyState({ action, body, onAction, title }) {
  return <div className="empty-state"><h2>{title}</h2><p>{body}</p>{action ? <button className="secondary-button" type="button" onClick={onAction}>{action}<Icon name="arrow" size={17} /></button> : null}</div>
}

function OverviewPanel({ analysis, onReview }) {
  const checks = analysis.ats_checks || []
  const scoredChecks = checks.filter(check => check.required !== false)
  const passed = scoredChecks.filter(check => check.matched)
  const attention = scoredChecks.filter(check => !check.matched)
  return <div className="overview-grid">
    <section><h2>Overview</h2>
      <dl className="overview-metrics">
        <div><dt>Pages</dt><dd>{analysis.candidate.page_count ?? '—'}</dd></div>
        <div><dt>Checks passed</dt><dd>{passed.length}<small> / {scoredChecks.length}</small></dd></div>
        <div><dt>Needs attention</dt><dd>{attention.length}</dd></div>
      </dl>
      <Breakdown sections={analysis.ats_section_scores || []} />
    </section>
    <section className="review-findings"><h3>Passed</h3>
      <ul>{passed.length ? passed.slice(0, 3).map(check => <li key={check.label}><Icon name="check" size={16} /><span>{check.success || check.label}</span></li>) : <li>No strengths confirmed by these checks.</li>}</ul>
      <h3>Fix next</h3><ul>{attention.length ? attention.slice(0, 3).map(check => <li key={check.label}><Icon name="alert" size={16} /><span>{check.label}</span></li>) : <li>Review the language in your experience section.</li>}</ul>
      <button type="button" className="text-button" onClick={() => onReview(attention.length ? 'ats' : 'suggestions')}>Review findings <Icon name="arrow" size={16} /></button>
    </section>
  </div>
}

function AtsPanel({ analysis }) {
  const checks = analysis.ats_checks || []
  return <div className="detail-panel">
    <header className="panel-heading"><h2>Resume checks</h2><p>Sections detected in the uploaded PDF.</p></header>
    {[{label:'Needs attention', items:checks.filter(check => !check.matched && check.required !== false)}, {label:'Passed', items:checks.filter(check => check.matched)}].map(group =>
      <section className="check-group" key={group.label}><h3>{group.label} <span className="count">{group.items.length}</span></h3>
        {group.items.length ? group.items.map(check => <details className="check-disclosure" key={check.label}>
          <summary><Icon name={check.matched ? 'check' : 'alert'} size={17} /><span>{check.label}</span><Icon name="chevron" size={16} /></summary>
          <p>{check.matched ? check.success : check.warning}</p><small>{check.required === false ? 'Optional section' : `Weight in structure score: ${check.weight} points`}</small>
        </details>) : <p className="panel-description">No checks in this group.</p>}
      </section>
    )}
  </div>
}

function SuggestionsPanel({ analysis, onPreview, drafts, setDrafts }) {
  const findings = analysis.bullet_quality?.flagged_bullets || []
  const [selected, setSelected] = useState(0)
  const [mobile, setMobile] = useState(() => window.matchMedia('(max-width: 639px)').matches)
  const [editorOpen, setEditorOpen] = useState(false)
  const editorDialog = useRef(null)
  useEffect(() => {
    const query = window.matchMedia('(max-width: 639px)')
    const update = () => { setMobile(query.matches); setEditorOpen(false) }
    query.addEventListener('change', update)
    return () => query.removeEventListener('change', update)
  }, [])
  useEffect(() => { if (mobile && editorOpen) editorDialog.current?.showModal() }, [mobile, editorOpen])
  const [skipped, setSkipped] = useState([])
  const [copyStatus, setCopyStatus] = useState('')
  const finding = findings[selected]
  const draft = finding ? drafts[selected] ?? finding.suggestion ?? '' : ''
  async function copyDraft() {
    try { await navigator.clipboard.writeText(draft); setCopyStatus('Copied. Paste it into your resume editor.') }
    catch { setCopyStatus('Copy unavailable. Select and copy the draft below.') }
  }
  if (!finding) return <EmptyState title="No specific rewrites found" body="The current analysis did not return a bullet to revise. Check the ATS and keyword findings for other changes." />
  const editor = <section className="draft-editor" aria-label="Selected suggestion">
        <div className="editor-heading"><h3>Experience wording</h3><button type="button" className="text-button" onClick={onPreview}>View resume</button></div>
        <p className="field-label">Current wording</p><blockquote>{finding.original}</blockquote>
        <p className="field-label">Why review it</p><p>{finding.coaching_tip || (finding.issues || []).join(' · ') || 'Make the action and outcome clearer.'}</p>
        <label className="field-label" htmlFor="suggestion-draft">Your draft</label>
        <textarea id="suggestion-draft" value={draft} onChange={event => { setDrafts({...drafts, [selected]:event.target.value}); setCopyStatus('') }} rows="5" aria-describedby="draft-help" />
        <small id="draft-help">Local draft only. This does not change the uploaded PDF. Replace any placeholders with verified facts.</small>
        <div className="draft-actions"><button type="button" className="primary-button" disabled={!draft.trim()} onClick={copyDraft}>Copy draft <Icon name="file" size={16} /></button>
          <button type="button" className="secondary-button" onClick={() => setSkipped(skipped.includes(selected) ? skipped.filter(index => index !== selected) : [...skipped, selected])}>{skipped.includes(selected) ? 'Undo skip' : 'Skip for now'}</button></div>
        <p className="field-help" role="status">{copyStatus || (skipped.includes(selected) ? 'Skipped for this review. You can restore it.' : '')}</p>
      </section>
  return <div className="detail-panel">
    <header className="panel-heading"><h2>Improve bullet wording</h2><p>Keep only wording you can support.</p></header>
    <div className="edit-workspace">
      <div className="edit-list" role="group" aria-label="Choose feedback">{findings.map((item, index) =>
        <button type="button" className={selected === index ? 'edit-choice is-selected' : 'edit-choice'} aria-pressed={selected === index} key={index} onClick={() => { setSelected(index); setCopyStatus(''); if (mobile) setEditorOpen(true) }}>
          <small title={item.original}>{skipped.includes(index) ? 'Skipped · ' : ''}{item.original}</small><Icon name="chevron" size={16} />
        </button>)}
      </div>
      {mobile ? <><p className="panel-description">Select a bullet to open the editor.</p><dialog className="editor-dialog" ref={editorDialog} aria-label="Improve wording" onClose={() => setEditorOpen(false)}><div className="editor-dialog-header"><strong>Improve wording</strong><button type="button" className="secondary-button" onClick={() => editorDialog.current?.close()}>Done <Icon name="close" size={16} /></button></div>{editor}</dialog></> : editor}
    </div>
  </div>
}

function KeywordsPanel({ analysis, onEdit }) {
  const jobProvided = Boolean(analysis.job_description?.trim())
  if (!jobProvided) return <EmptyState action="Add job description" body="Paste the responsibilities and requirements from a real job post. Your PDF does not need to be uploaded again." onAction={onEdit} title="Keyword matching needs a target role" />
  const requirements = analysis.requirement_evidence?.requirements || []
  const missingByGroup = analysis.gap_explainer?.categorized_missing_keywords || {}
  return (
    <div className="detail-panel">
      <div className="detail-panel__intro"><h2>Job match</h2><p>{analysis.requirement_evidence?.summary}</p></div>
      <section className="evidence-list" aria-label="Role requirement evidence">
        {requirements.map((item) => (
          <article className={item.status === 'Matched' ? 'evidence-row evidence-row--match' : 'evidence-row evidence-row--missing'} key={item.requirement}>
            <span><Icon name={item.status === 'Matched' ? 'check' : 'alert'} size={17} /></span>
            <div><h3>{item.requirement}</h3><p>{item.evidence || 'No supporting line was found in the parsed resume.'}</p></div>
            <strong>{item.status}</strong>
          </article>
        ))}
      </section>
      {Object.keys(missingByGroup).length ? (
        <section className="gap-groups"><h2>Missing signals by type</h2><div>{Object.entries(missingByGroup).map(([group, items]) => <article key={group}><h3>{group}</h3><p>{items.join(' · ')}</p></article>)}</div></section>
      ) : null}
    </div>
  )
}


function PdfPreview({ file, previewUrl }) {
  return (
    <div className="pdf-preview">
      <a className="text-button" href={previewUrl} target="_blank" rel="noreferrer">Open PDF in new tab <Icon name="external" size={16} /></a>
      <object className="pdf-object" data={previewUrl} type="application/pdf" title={`Preview of ${file.name}`}><p>Your browser cannot embed this PDF. Use the link above to open it.</p></object>
      <p className="mobile-preview-note">Open the PDF in a new tab to read it with your device’s document viewer.</p>
    </div>
  )
}

export default function ResultsView({
  activeTab, analysis, file, headingRef, onDownload, onEdit, onReplace,
  onTabChange, previewUrl, reportError, reportStage, suggestionDrafts, onDraftsChange,
}) {
  const dialogRef = useRef(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const tabRefs = useRef([])
  useEffect(() => { if (previewOpen) dialogRef.current?.showModal() }, [previewOpen])
  const score = scoreValue(analysis.summary.resume_score)
  const missing = (analysis.ats_checks || []).filter(check => !check.matched && check.required !== false).sort((a, b) => b.weight - a.weight)
  const finding = analysis.bullet_quality?.flagged_bullets?.[0]
  const priority = finding?.issues?.[0] || missing[0]?.label || 'Compare with a target role'
  const nextTab = finding ? 'suggestions' : missing.length ? 'ats' : 'keywords'
  const roleProvided = Boolean(analysis.job_description?.trim())
  function selectTab(id, focus = false) {
    onTabChange(id)
    if (focus) tabRefs.current[sections.findIndex(section => section.id === id)]?.focus()
  }
  function onTabKey(event, index) {
    let next
    if (event.key === 'ArrowRight') next = (index + 1) % sections.length
    if (event.key === 'ArrowLeft') next = (index + sections.length - 1) % sections.length
    if (event.key === 'Home') next = 0
    if (event.key === 'End') next = sections.length - 1
    if (next !== undefined) { event.preventDefault(); selectTab(sections[next].id, true) }
  }
  return <article className="report" aria-labelledby="results-title">
    <header className="report-heading">
      <div><p className="workflow-status">{activeTab === 'suggestions' ? 'Editing suggestion' : 'Analysis complete'}</p><h1 id="results-title" ref={headingRef} tabIndex="-1">{file.name}</h1><p className="document-meta">PDF · {Math.ceil(file.size / 1024).toLocaleString()} KB · {analysis.candidate.page_count ?? '—'} {analysis.candidate.page_count === 1 ? 'page' : 'pages'}</p></div>
      <div className="report-tools"><button type="button" className="secondary-button" onClick={onReplace}>Replace PDF</button><button type="button" className="primary-button" onClick={onDownload} disabled={reportStage === 'downloading'}><Icon name="download" size={17} />{reportStage === 'downloading' ? 'Preparing…' : 'Download report'}</button></div>
    </header>
    {reportError ? <p className="message message--error" role="alert">{reportError}</p> : null}
    <section className="result-summary" aria-label="Analysis summary">
      <div className="summary-score"><span>Resume structure</span><div><strong>{score ?? '—'}</strong><span>/ 100</span></div><small>Based on section checks</small></div>
      <div className="summary-priority"><span className="priority-label">Fix first</span><h2>{priority}</h2><p>{finding?.coaching_tip || missing[0]?.warning || 'Add a job description to compare requirements.'}</p><button type="button" className="text-button" onClick={() => selectTab(nextTab, true)}>{nextTab === 'suggestions' ? 'Edit this bullet' : nextTab === 'ats' ? 'View this check' : 'Add job description'} <Icon name="arrow" size={16} /></button></div>
    </section>
    <div className="mobile-context-actions"><button type="button" className="secondary-button" onClick={() => setPreviewOpen(true)}>View resume</button><button type="button" className="secondary-button" onClick={() => roleProvided ? selectTab('keywords', true) : onEdit()}>Job match</button></div>
    <div className="results-layout">
      <div className="analysis-workspace">
        <div className="analysis-tabs" role="tablist" aria-label="Analysis views">{sections.map((section,index) => <button key={section.id} ref={element => { tabRefs.current[index] = element }} id={'tab-'+section.id} type="button" role="tab" aria-selected={activeTab === section.id} aria-controls={'panel-'+section.id} tabIndex={activeTab === section.id ? 0 : -1} onClick={() => selectTab(section.id)} onKeyDown={event => onTabKey(event,index)}>{section.label}</button>)}</div>
        <section id="panel-overview" role="tabpanel" aria-labelledby="tab-overview" tabIndex="0" hidden={activeTab !== 'overview'}><OverviewPanel analysis={analysis} onReview={id => selectTab(id,true)} /></section>
        <section id="panel-ats" role="tabpanel" aria-labelledby="tab-ats" tabIndex="0" hidden={activeTab !== 'ats'}><AtsPanel analysis={analysis} /></section>
        <section id="panel-suggestions" role="tabpanel" aria-labelledby="tab-suggestions" tabIndex="0" hidden={activeTab !== 'suggestions'}><SuggestionsPanel analysis={analysis} onPreview={() => setPreviewOpen(true)} drafts={suggestionDrafts} setDrafts={onDraftsChange} /></section>
        <section id="panel-keywords" role="tabpanel" aria-labelledby="tab-keywords" tabIndex="0" hidden={activeTab !== 'keywords'}><KeywordsPanel analysis={analysis} onEdit={onEdit} /></section>
      </div>
      <aside className="context-panel" aria-label="Resume context">
        <section className="document-tool"><Icon name="file" size={26} /><h2>Your original resume</h2><p>Check each finding against the document you uploaded.</p><button type="button" className="secondary-button" onClick={() => setPreviewOpen(true)}>View resume <Icon name="external" size={16} /></button></section>
        <section className="role-tool"><h2>Job match</h2>{roleProvided ? <><p className="role-score">{scoreValue(analysis.summary.semantic_match_score) ?? '—'}<small>{analysis.summary.semantic_match_score == null ? ' Not available' : '% role similarity'}</small></p><p className="role-excerpt">{analysis.job_description}</p><button type="button" className="text-button" onClick={() => selectTab('keywords',true)}>View match <Icon name="arrow" size={16} /></button><button type="button" className="text-button" onClick={onEdit}>Edit job description</button></> : <><p>Compare your resume with a job description.</p><button type="button" className="secondary-button" onClick={onEdit}>Add job description</button></>}</section>
      </aside>
    </div>
    <dialog className="preview-dialog" ref={dialogRef} aria-labelledby="preview-title" onClose={() => setPreviewOpen(false)} onClick={event => { if (event.target === event.currentTarget) dialogRef.current?.close() }}>
      <div className="preview-dialog__header"><h2 id="preview-title">Original resume</h2><button className="secondary-button" type="button" onClick={() => dialogRef.current?.close()}>Close <Icon name="close" size={17} /></button></div>
      {previewOpen ? <PdfPreview file={file} previewUrl={previewUrl} /> : null}
    </dialog>
  </article>
}
