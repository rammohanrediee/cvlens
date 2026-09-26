import { useEffect, useRef, useState } from 'react'
import { analyzeResume, checkHealth, downloadReport, extractResume } from './api.js'
import AppHeader from './components/AppHeader.jsx'
import ResultsView from './components/ResultsView.jsx'
import UploadView from './components/UploadView.jsx'

const MAX_PDF_BYTES = 5 * 1024 * 1024
const MIN_JOB_DESCRIPTION_LENGTH = 30

function initialTheme() {
  const current = document.documentElement.dataset.theme
  if (current === 'light' || current === 'dark') return current
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function fileKey(file) {
  return file ? `${file.name}:${file.size}:${file.lastModified}` : ''
}

function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [useAiAnalysis, setUseAiAnalysis] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [analysisPayload, setAnalysisPayload] = useState(null)
  const [error, setError] = useState('')
  const [stage, setStage] = useState('idle')
  const [serviceStatus, setServiceStatus] = useState('checking')
  const [currentView, setCurrentView] = useState('analyze')
  const [activeTab, setActiveTab] = useState('overview')
  const [reportStage, setReportStage] = useState('idle')
  const [reportError, setReportError] = useState('')
  const [suggestionDrafts, setSuggestionDrafts] = useState({})
  const [theme, setTheme] = useState(initialTheme)
  const extractionCache = useRef({ key: '', data: null })
  const activeRequest = useRef(0)
  const abortController = useRef(null)
  const resultsHeading = useRef(null)
  const fileInput = useRef(null)
  const previewUrlRef = useRef('')
  const replaceRequested = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    checkHealth({ signal: controller.signal }).then(() => setServiceStatus('connected')).catch((requestError) => {
      if (requestError.name !== 'AbortError') setServiceStatus('offline')
    })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.style.colorScheme = theme
    try { window.localStorage.setItem('cvlens-theme', theme) } catch { /* Storage may be unavailable. */ }
  }, [theme])

  useEffect(() => () => {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current)
  }, [])

  useEffect(() => {
    if (currentView === 'results') resultsHeading.current?.focus({ preventScroll: true })
  }, [currentView])

  useEffect(() => {
    if (!replaceRequested.current || currentView !== 'analyze') return
    fileInput.current?.click()
    replaceRequested.current = false
  }, [currentView])

  function setDocumentPreview(selectedFile) {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current)
    const nextUrl = selectedFile ? URL.createObjectURL(selectedFile) : ''
    previewUrlRef.current = nextUrl
    setPreviewUrl(nextUrl)
  }

  function selectFile(selectedFile) {
    setSuggestionDrafts({})
    setError('')
    setReportError('')
    setAnalysis(null)
    setAnalysisPayload(null)
    setCurrentView('analyze')
    setActiveTab('overview')
    setStage('idle')
    extractionCache.current = { key: '', data: null }
    if (!selectedFile) {
      setFile(null)
      setDocumentPreview(null)
      return
    }
    if (selectedFile.type !== 'application/pdf' && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setFile(null)
      setDocumentPreview(null)
      if (fileInput.current) fileInput.current.value = ''
      setError('Choose a PDF resume. DOC and DOCX files are not supported yet.')
      return
    }
    if (selectedFile.size > MAX_PDF_BYTES) {
      setFile(null)
      setDocumentPreview(null)
      if (fileInput.current) fileInput.current.value = ''
      setError('Choose a PDF no larger than 5 MiB.')
      return
    }
    setFile(selectedFile)
    setDocumentPreview(selectedFile)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setReportError('')
    if (!file) {
      setError('Add your resume PDF before starting the analysis.')
      fileInput.current?.focus()
      return
    }
    const trimmedJobDescription = jobDescription.trim()
    if (trimmedJobDescription.length > 0 && trimmedJobDescription.length < MIN_JOB_DESCRIPTION_LENGTH) {
      setError('Use at least 30 characters for the job description, or leave it blank for a resume-only review.')
      document.getElementById('job-description')?.focus()
      return
    }
    const requestId = activeRequest.current + 1
    activeRequest.current = requestId
    abortController.current?.abort()
    const controller = new AbortController()
    abortController.current = controller

    try {
      const selectedKey = fileKey(file)
      let extraction = extractionCache.current.key === selectedKey ? extractionCache.current.data : null
      if (!extraction) {
        setStage('extracting')
        extraction = await extractResume(file, { signal: controller.signal })
        extractionCache.current = { key: selectedKey, data: extraction }
      }
      setStage('analyzing')
      const payload = {
        resume_text: extraction.text,
        resume_skills: [],
        job_description: trimmedJobDescription,
        page_count: extraction.page_count,
        use_ai_analysis: useAiAnalysis,
      }
      const result = await analyzeResume(payload, { signal: controller.signal })
      if (activeRequest.current !== requestId) return
      setAnalysis(result)
      setSuggestionDrafts({})
      setAnalysisPayload(payload)
      setServiceStatus('connected')
      setStage('complete')
      setActiveTab('overview')
      setCurrentView('results')
      window.scrollTo({ top: 0 })
    } catch (requestError) {
      if (requestError.name === 'AbortError' || activeRequest.current !== requestId) return
      setError(requestError.message)
      if (requestError.code === 'offline') setServiceStatus('offline')
      setStage('error')
    }
  }

  async function handleReportDownload() {
    if (!analysisPayload || reportStage === 'downloading') return
    setReportError('')
    setReportStage('downloading')
    try {
      const report = await downloadReport(analysisPayload)
      const reportUrl = URL.createObjectURL(report)
      const link = document.createElement('a')
      const baseName = file.name.replace(/\.pdf$/i, '')
      link.href = reportUrl
      link.download = `${baseName}-analysis-report.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(reportUrl), 0)
      setReportStage('complete')
    } catch (requestError) {
      setReportError(requestError.message)
      setReportStage('error')
    }
  }

  function resetSession() {
    setSuggestionDrafts({})
    activeRequest.current += 1
    abortController.current?.abort()
    extractionCache.current = { key: '', data: null }
    if (fileInput.current) fileInput.current.value = ''
    setDocumentPreview(null)
    setFile(null)
    setJobDescription('')
    setUseAiAnalysis(false)
    setAnalysis(null)
    setAnalysisPayload(null)
    setError('')
    setStage('idle')
    setCurrentView('analyze')
    setActiveTab('overview')
    setReportStage('idle')
    setReportError('')
  }

  function navigate(view) {
    if (view === 'results' && !analysis) return
    setCurrentView(view)
    window.scrollTo({ top: 0 })
  }

  function replaceFile() {
    replaceRequested.current = true
    setCurrentView('analyze')
    window.scrollTo({ top: 0 })
  }

  const busy = stage === 'extracting' || stage === 'analyzing'
  const stageMessage = stage === 'extracting' ? 'Reading PDF…' : stage === 'analyzing' ? 'Analyzing evidence…' : ''

  return (
    <div className="app-shell">
      <AppHeader onNavigate={navigate} onJobMatch={() => {
        if (analysis) { setActiveTab('keywords'); navigate('results') }
        else { navigate('analyze'); document.getElementById('job-description')?.focus() }
      }} theme={theme} onThemeChange={() => setTheme(current => current === 'dark' ? 'light' : 'dark')} />
      <main className="app-content" id="app-content">
        {currentView === 'analyze' ? (
          <UploadView
            analysisExists={Boolean(analysis)}
            busy={busy}
            error={error}
            file={file}
            inputRef={fileInput}
            jobDescription={jobDescription}
            useAiAnalysis={useAiAnalysis}
            onFileSelect={selectFile}
            onJobChange={setJobDescription}
            onUseAiAnalysisChange={setUseAiAnalysis}
            onReset={resetSession}
            onSubmit={handleSubmit}
            onViewResults={() => navigate('results')}
            serviceStatus={serviceStatus}
            stageMessage={stageMessage}
          />
        ) : (
          <ResultsView
            activeTab={activeTab}
            suggestionDrafts={suggestionDrafts}
            onDraftsChange={setSuggestionDrafts}
            analysis={analysis}
            file={file}
            headingRef={resultsHeading}
            onDownload={handleReportDownload}
            onEdit={() => navigate('analyze')}
            onReplace={replaceFile}
            onTabChange={setActiveTab}
            previewUrl={previewUrl}
            reportError={reportError}
            reportStage={reportStage}
          />
        )}
      </main>
      <footer className="product-footer"><span>cvLens</span><a href="https://github.com/rammohanrediee/cvlens" target="_blank" rel="noreferrer">GitHub ↗</a></footer>
    </div>
  )
}

export default App
