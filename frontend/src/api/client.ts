function getDefaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://127.0.0.1:8000/api'
  }

  return `${window.location.protocol}//${window.location.hostname}:8000/api`
}

function getCandidateApiBaseUrls() {
  const explicit = import.meta.env.VITE_API_BASE_URL?.trim()
  if (explicit) {
    return [explicit]
  }

  const defaults = new Set<string>([getDefaultApiBaseUrl()])
  if (typeof window !== 'undefined') {
    defaults.add(`${window.location.protocol}//127.0.0.1:8000/api`)
    defaults.add(`${window.location.protocol}//localhost:8000/api`)
  }

  return Array.from(defaults)
}

type ValidationIssue = {
  loc?: Array<string | number>
  msg?: string
}

function getErrorMessage(payload: unknown, status: number) {
  if (typeof payload !== 'object' || payload === null) {
    return `Request failed (${status})`
  }

  const detail = (payload as { detail?: unknown }).detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        const issue = item as ValidationIssue
        const location = Array.isArray(issue.loc) ? issue.loc.slice(1).join('.') : ''
        const message = issue.msg ?? 'Invalid value'
        return location ? `${location}: ${message}` : message
      })
      .filter(Boolean)

    if (messages.length > 0) {
      return messages.join(' | ')
    }
  }

  return `Request failed (${status})`
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  accessToken?: string
): Promise<T> {
  const headers = new Headers(options.headers ?? {})
  headers.set('Content-Type', 'application/json')

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  let response: Response | null = null
  let lastError: unknown = null

  for (const baseUrl of getCandidateApiBaseUrls()) {
    try {
      response = await fetch(`${baseUrl}${path}`, {
        ...options,
        headers,
      })
      break
    } catch (error) {
      lastError = error
    }
  }

  if (!response) {
    const message =
      lastError instanceof Error
        ? `${lastError.message}. Tried: ${getCandidateApiBaseUrls().join(', ')}`
        : 'API unreachable. Check that the backend is running on port 8000.'
    throw new Error(message)
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(getErrorMessage(payload, response.status))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}
