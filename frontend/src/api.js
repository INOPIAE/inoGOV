const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export const apiBase = BASE

let token = localStorage.getItem('token')
let onUnauthorized = () => {}
let onOtpSetupRequired = () => {}

export function setToken(value) {
  token = value
  if (value) localStorage.setItem('token', value)
  else localStorage.removeItem('token')
}

export function getToken() {
  return token
}

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

export function setOtpSetupHandler(handler) {
  onOtpSetupRequired = handler
}

export class ApiError extends Error {
  constructor(status, detail, retryAfter) {
    super(detail || `HTTP ${status}`)
    this.status = status
    this.detail = detail
    this.retryAfter = retryAfter
  }
}

export async function api(path, { method = 'GET', body, params, auth = true } = {}) {
  const url = new URL(BASE + path)
  for (const [key, value] of Object.entries(params || {})) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value)
  }
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth && token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'network')
  }
  if (response.status === 204) return null

  let data = null
  try {
    data = await response.json()
  } catch {
    // leerer oder nicht-JSON Body
  }
  if (!response.ok) {
    if (response.status === 401 && auth && token) onUnauthorized()
    if (response.status === 403 && data?.detail === 'otp_setup_required') onOtpSetupRequired()
    const detail = typeof data?.detail === 'string' ? data.detail : undefined
    throw new ApiError(response.status, detail, Number(response.headers.get('Retry-After')) || undefined)
  }
  return data
}
