const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, code = 'request_failed', options = {}) {
    super(message, options)
    this.name = 'ApiError'
    this.code = code
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new ApiError('The analysis service is unavailable. Start the backend and try again.', 'offline', { cause: error })
  }

  if (!response.ok) {
    let message = 'The request could not be completed. Try again.'
    let code = 'request_failed'
    try {
      const payload = await response.json()
      message = payload.error?.message || payload.detail?.message || message
      code = payload.error?.code || payload.detail?.code || code
    } catch {
      // Intermediaries may return HTML or an empty response. Keep a safe message.
    }
    throw new ApiError(message, code)
  }
  return response
}

export async function checkHealth({ signal } = {}) {
  const response = await request('/api/v1/health', { signal })
  return (await response.json()).data
}

export async function extractResume(file, { signal } = {}) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await request('/api/v1/documents/extract', { method: 'POST', body: formData, signal })
  return (await response.json()).data
}

export async function analyzeResume(payload, { signal } = {}) {
  const response = await request('/api/v1/analyses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })
  return (await response.json()).data
}

export async function downloadReport(payload, { signal } = {}) {
  const response = await request('/api/v1/reports/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })
  return response.blob()
}
