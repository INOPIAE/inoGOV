import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { getToken, setToken } from '../api'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { mockFetch } from '../test-utils'

const ME = { id: '1', username: 'marcus', email: 'm@example.com', roles: ['user'] }

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

describe('auth store', () => {
  it('logs in, stores the token and loads the user', async () => {
    const fetch = mockFetch({
      'POST /auth/login': { body: { access_token: 'tok' } },
      'GET /users/me': { body: ME },
    })
    const auth = useAuthStore()
    await auth.login('marcus', 'pw', '')
    expect(getToken()).toBe('tok')
    expect(auth.isLoggedIn).toBe(true)
    expect(auth.canEdit).toBe(true)
    expect(auth.isAdmin).toBe(false)
    expect(fetch.calls[0].body).toEqual({ username: 'marcus', password: 'pw', otp: null })
  })

  it('does not log in when the server asks for an OTP', async () => {
    mockFetch({ 'POST /auth/login': { status: 401, body: { detail: 'otp_required' } } })
    const auth = useAuthStore()
    await expect(auth.login('marcus', 'pw')).rejects.toMatchObject({ status: 401, detail: 'otp_required' })
    expect(auth.isLoggedIn).toBe(false)
  })

  it('logout clears token and user', async () => {
    mockFetch({ 'GET /users/me': { body: { ...ME, roles: ['admin'] } } })
    setToken('tok')
    const auth = useAuthStore()
    await auth.init()
    expect(auth.isAdmin).toBe(true)
    auth.logout()
    expect(getToken()).toBeNull()
    expect(auth.isLoggedIn).toBe(false)
  })

  it('init drops an invalid token', async () => {
    mockFetch({ 'GET /users/me': { status: 401, body: {} } })
    setToken('stale')
    const auth = useAuthStore()
    await auth.init()
    expect(auth.ready).toBe(true)
    expect(getToken()).toBeNull()
  })
})

describe('settings store', () => {
  it('prefers the name in the requested language', () => {
    const settings = useSettingsStore()
    settings.sprachen = [
      { id: 'a', sprache2: 'de' },
      { id: 'b', sprache2: 'en' },
    ]
    const namen = [
      { sprache_id: 'a', ortsname: 'Lemberg' },
      { sprache_id: 'b', ortsname: 'Lviv' },
    ]
    expect(settings.pickName(namen, 'ortsname', 'en')).toBe('Lviv')
    expect(settings.pickName(namen, 'ortsname', 'de')).toBe('Lemberg')
    expect(settings.pickName(namen, 'ortsname', 'pl')).toBe('Lemberg')
    expect(settings.pickName([], 'ortsname', 'de')).toBe('')
  })
})
