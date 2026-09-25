import { useState } from 'react'
import { Icon } from './Icon.jsx'

export default function UploadView({
  analysisExists, busy, candidateName, error, file, inputRef, jobDescription,
  onCandidateChange, onFileSelect, onJobChange, onReset, onSubmit, onViewResults, serviceStatus, stageMessage,
}) {
  const [dragging, setDragging] = useState(false)
  const [jobTouched, setJobTouched] = useState(false)
  const jobInvalid = jobDescription.trim().length > 0 && jobDescription.trim().length < 30
  const showJobError = jobInvalid && (jobTouched || Boolean(error))

  function handleDrop(event) {
    event.preventDefault()
    setDragging(false)
    if (!busy && event.dataTransfer.files?.length) onFileSelect(event.dataTransfer.files[0])
  }

  return (
    <section className="submission" aria-labelledby="upload-title">
      <ol className="workflow" aria-label="Analysis progress"><li aria-current={busy ? undefined : 'step'}>Upload</li><li aria-current={busy ? 'step' : undefined}>Analyze</li><li>Review</li></ol>
      <header className="submission-intro">
        <h1 id="upload-title">Your next move starts here.</h1>
        <p>Upload your resume. Get a clear picture of what to improve.</p>
      </header>

      <form className="review-form" onSubmit={onSubmit} noValidate aria-busy={busy}>
        <div className="field-heading"><label htmlFor="resume-file">Your resume</label><span>PDF · 5 MiB max · 20 pages max</span></div>
        <div
          className={`attachment${file ? ' attachment--selected' : ''}${dragging ? ' attachment--dragging' : ''}`}
          onDragEnter={(event) => { event.preventDefault(); if (!busy) setDragging(true) }}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setDragging(false) }}
          onDrop={handleDrop}
          data-disabled={busy || undefined}
        >
          <input ref={inputRef} className="visually-hidden" id="resume-file" type="file" accept="application/pdf,.pdf" onChange={(event) => { if (event.target.files?.[0]) onFileSelect(event.target.files[0]) }} disabled={busy} aria-describedby="file-help" />
          <Icon name={file ? 'check' : 'file'} size={24} />
          <div className="attachment-copy"><strong>{file ? file.name : 'Drop your resume here'}</strong><span>{file ? `${Math.ceil(file.size / 1024).toLocaleString()} KB · Ready for review` : 'or select one from your device'}</span></div>
          <label className="secondary-button attachment-button" htmlFor="resume-file" aria-disabled={busy}>{file ? 'Replace PDF' : 'Choose PDF'}<Icon name={file ? 'replace' : 'arrow'} size={17} /></label>
        </div>
        <p className="field-help" id="file-help">PDF only. Your upload is processed without saving the document.</p>

        <div className="job-field">
          <div className="field-heading"><label htmlFor="job-description">Target job description</label><span>Optional</span></div>
          <textarea id="job-description" value={jobDescription} onChange={(event) => onJobChange(event.target.value)} onBlur={() => setJobTouched(true)} rows="3" maxLength="20000" placeholder="Paste the job description" aria-describedby="job-help" aria-invalid={showJobError} disabled={busy} />
          <p className={showJobError ? 'field-help field-help--error' : 'field-help'} id="job-help">{showJobError ? 'Use at least 30 characters, or leave this field blank.' : 'Add a job description to compare skills and experience with the role.'}</p>
        </div>

        <details className="label-disclosure" open={candidateName ? true : undefined}>
          <summary>Review settings <span>Optional</span><Icon name="chevron" size={16} /></summary>
          <div className="field-group">
            <label htmlFor="candidate-name">Analysis label</label>
            <input id="candidate-name" type="text" value={candidateName} onChange={(event) => onCandidateChange(event.target.value)} maxLength="120" autoComplete="name" placeholder="Candidate name" disabled={busy} />
          </div>
        </details>

        <div className="submission-status" aria-live="polite">
          {error ? <p className="message message--error"><Icon name="alert" size={18} /><span>{error}</span></p> : null}
          {busy ? <p className="message"><Icon name="file" size={18} /><span>{stageMessage}</span></p> : null}
          {serviceStatus === 'offline' ? <p className="message message--error"><Icon name="alert" size={18} /><span>The analysis service is unavailable. Please try again shortly.</span></p> : null}
        </div>
        <div className="submission-actions">
          <div><button className="primary-button" type="submit" disabled={!file || busy || serviceStatus === 'offline'}>{busy ? stageMessage : analysisExists ? 'Analyze again' : 'Analyze resume'}{!busy ? <Icon name="arrow" size={18} /> : null}</button>{!file ? <small>Choose a PDF to start.</small> : null}</div>
          {analysisExists ? <div className="draft-actions"><button className="secondary-button" type="button" onClick={onViewResults} disabled={busy}>Back to results</button><button className="text-button" type="button" onClick={onReset} disabled={busy}>Reset session</button></div> : <p>Section checks · Suggested edits · PDF report</p>}
        </div>
      </form>
    </section>
  )
}
