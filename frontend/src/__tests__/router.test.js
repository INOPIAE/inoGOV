import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { setToken } from '../api'
import { createAppRouter } from '../router'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { mockFetch } from '../test-utils'

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

async function go(path) {
  const router = createAppRouter(createMemoryHistory())
  await router.push(path)
  return router.currentRoute.value
}

describe('router guard', () => {
  it('lets anonymous visitors search when search is public', async () => {
    useSettingsStore().publicSearch = true
    expect((await go('/')).path).toBe('/')
  })

  it('redirects anonymous visitors to login when search is restricted', async () => {
    useSettingsStore().publicSearch = false
    const route = await go('/')
    expect(route.path).toBe('/login')
    expect(route.query.next).toBe('/')
  })

  it('lets signed-in users search when search is restricted', async () => {
    useSettingsStore().publicSearch = false
    useAuthStore().user = { username: 'm', roles: ['user'] }
    expect((await go('/')).path).toBe('/')
  })

  it('keeps public pages reachable when search is restricted', async () => {
    useSettingsStore().publicSearch = false
    for (const path of ['/login', '/about', '/imprint', '/privacy', '/terms', '/license', '/third-party-licenses', '/forgot-password']) {
      expect((await go(path)).path).toBe(path)
    }
  })

  it('protects management routes by role', async () => {
    const auth = useAuthStore()
    expect((await go('/manage/orte')).path).toBe('/login')
    auth.user = { username: 'm', roles: ['user'] }
    expect((await go('/manage/orte')).path).toBe('/manage/orte')
    expect((await go('/users')).path).toBe('/')
    auth.user = { username: 'a', roles: ['admin'] }
    expect((await go('/users')).path).toBe('/users')
  })
})

describe('settings store loading', () => {
  it('reads the search mode from the public settings without a token', async () => {
    const fetch = mockFetch({
      'GET /settings': { body: { app_name: 'X', copyright_name: 'Y', public_search: false } },
    })
    setToken('tok')
    const settings = useSettingsStore()
    await settings.load()
    expect(settings.publicSearch).toBe(false)
    expect(settings.appName).toBe('X')
    expect(fetch.calls).toHaveLength(1)
    expect(fetch.calls[0].headers.Authorization).toBeUndefined()
  })

  it('loads reference data once and only on demand', async () => {
    const fetch = mockFetch({ 'GET /sprachen': { body: [{ id: 's' }] }, 'GET /kreise': { body: [] } })
    const settings = useSettingsStore()
    await settings.loadReference()
    await settings.loadReference()
    expect(fetch.calls.filter((c) => c.key === 'GET /sprachen')).toHaveLength(1)
    expect(settings.sprachen).toEqual([{ id: 's' }])
  })
})
