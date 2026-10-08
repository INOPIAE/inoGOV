import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api, setToken, setUnauthorizedHandler } from '../api'
import { mockFetch } from '../test-utils'

afterEach(() => {
  setToken(null)
  setUnauthorizedHandler(() => {})
  vi.unstubAllGlobals()
})

describe('api', () => {
  it('sends JSON and the bearer token', async () => {
    const fetch = mockFetch({ 'POST /x': { body: { ok: true } } })
    setToken('abc')
    expect(await api('/x', { method: 'POST', body: { a: 1 } })).toEqual({ ok: true })
    expect(fetch.calls[0].body).toEqual({ a: 1 })
    expect(fetch.calls[0].headers.Authorization).toBe('Bearer abc')
  })

  it('omits the token when auth is false', async () => {
    const fetch = mockFetch({ 'GET /x': { body: {} } })
    setToken('abc')
    await api('/x', { auth: false })
    expect(fetch.calls[0].headers.Authorization).toBeUndefined()
  })

  it('adds query parameters and skips empty ones', async () => {
    const fetch = mockFetch({ 'GET /orte': { body: [] } })
    await api('/orte', { params: { q: 'abc', kreis_id: '', limit: 5 } })
    expect(fetch.calls[0].url.search).toBe('?q=abc&limit=5')
  })

  it('returns null for 204', async () => {
    mockFetch({ 'DELETE /x': { status: 204 } })
    expect(await api('/x', { method: 'DELETE' })).toBeNull()
  })

  it('throws ApiError with status, detail and retry-after', async () => {
    mockFetch({ 'POST /auth/login': { status: 423, body: { detail: 'locked' }, headers: { 'Retry-After': '120' } } })
    const error = await api('/auth/login', { method: 'POST', body: {} }).catch((e) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 423, detail: 'locked', retryAfter: 120 })
  })

  it('maps network failures to status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('fail')))
    await expect(api('/x')).rejects.toMatchObject({ status: 0 })
  })

  it('calls the unauthorized handler on 401 with a token', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    mockFetch({ 'GET /users/me': { status: 401, body: {} } })
    setToken('abc')
    await expect(api('/users/me')).rejects.toBeInstanceOf(ApiError)
    expect(handler).toHaveBeenCalledOnce()
  })

  it('does not call the handler on 401 without auth (login)', async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    mockFetch({ 'POST /auth/login': { status: 401, body: {} } })
    setToken('abc')
    await expect(api('/auth/login', { method: 'POST', body: {}, auth: false })).rejects.toBeInstanceOf(ApiError)
    expect(handler).not.toHaveBeenCalled()
  })
})
