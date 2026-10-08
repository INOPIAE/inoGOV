import { afterEach, describe, expect, it, vi } from 'vitest'
import { setToken } from '../api'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { mockFetch, mountView } from '../test-utils'
import AppFooter from '../components/AppFooter.vue'
import SideNav from '../components/SideNav.vue'
import LoginView from '../views/LoginView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import HomeView from '../views/HomeView.vue'

afterEach(() => {
  setToken(null)
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

async function signedIn(roles) {
  const { createPinia } = await import('pinia')
  const pinia = createPinia()
  const { setActivePinia } = await import('pinia')
  setActivePinia(pinia)
  useAuthStore().user = { username: 'marcus', roles }
  return pinia
}

describe('AppFooter', () => {
  it('shows anonymous state and copyright', async () => {
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2028-05-01'))
    const { wrapper, pinia } = await mountView(AppFooter)
    useSettingsStore(pinia).copyrightName = 'ACME'
    await wrapper.vm.$nextTick()
    expect(wrapper.get('[data-test=login-state]').text()).toBe('Not signed in')
    expect(wrapper.get('[data-test=copyright]').text()).toBe('\u00a9 2026\u20132028 ACME')
  })

  it('shows user and roles', async () => {
    const { wrapper } = await mountView(AppFooter, { pinia: await signedIn(['admin', 'user']) })
    expect(wrapper.get('[data-test=login-state]').text()).toBe('Signed in as marcus (admin, user)')
  })

  it('is translated to German', async () => {
    const { wrapper } = await mountView(AppFooter, { language: 'de' })
    expect(wrapper.get('[data-test=login-state]').text()).toBe('Nicht angemeldet')
  })

  it('shows only the start year in 2026', async () => {
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-12-01'))
    const { wrapper } = await mountView(AppFooter)
    expect(wrapper.get('[data-test=copyright]').text()).toContain('\u00a9 2026 ')
  })
})

describe('SideNav', () => {
  it('hides management and user items for anonymous visitors', async () => {
    const { wrapper } = await mountView(SideNav)
    const text = wrapper.text()
    expect(text).toContain('Search places')
    expect(text).toContain('Log in')
    expect(text).not.toContain('Management')
    expect(text).not.toContain('My account')
  })

  it('shows management for users but not user administration', async () => {
    const { wrapper } = await mountView(SideNav, { pinia: await signedIn(['user']) })
    expect(wrapper.text()).toContain('Districts')
    expect(wrapper.text()).toContain('My account')
    expect(wrapper.text()).not.toContain('User management')
    expect(wrapper.text()).toContain('Log out')
  })

  it('shows user administration for admins', async () => {
    const { wrapper } = await mountView(SideNav, { pinia: await signedIn(['admin']) })
    expect(wrapper.text()).toContain('User management')
  })

  it('hides the search link for anonymous visitors when search is restricted', async () => {
    const pinia = (await import('pinia')).createPinia()
    ;(await import('pinia')).setActivePinia(pinia)
    useSettingsStore().publicSearch = false
    const { wrapper } = await mountView(SideNav, { pinia })
    expect(wrapper.text()).not.toContain('Search places')
  })

  it('keeps the search link for signed-in users when search is restricted', async () => {
    const pinia = await signedIn(['user'])
    useSettingsStore().publicSearch = false
    const { wrapper } = await mountView(SideNav, { pinia })
    expect(wrapper.text()).toContain('Search places')
  })
})

describe('LoginView', () => {
  it('asks for the OTP only when the server requires it', async () => {
    let attempts = 0
    mockFetch({
      'POST /auth/login': () =>
        ++attempts === 1 ? { status: 401, body: { detail: 'otp_required' } } : { body: { access_token: 'tok' } },
      'GET /users/me': { body: { username: 'marcus', roles: ['user'] } },
    })
    const { wrapper, router } = await mountView(LoginView, { route: '/login' })
    expect(wrapper.find('#otp').exists()).toBe(false)

    await wrapper.get('#username').setValue('marcus')
    await wrapper.get('#password').setValue('geheim123')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('#otp').exists()).toBe(true))

    await wrapper.get('#otp').setValue('123456')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(router.currentRoute.value.path).toBe('/'))
    expect(useAuthStore().isLoggedIn).toBe(true)
  })

  it('shows an error for wrong credentials without asking for OTP', async () => {
    mockFetch({ 'POST /auth/login': { status: 401, body: { detail: 'x' } } })
    const { wrapper } = await mountView(LoginView, { route: '/login' })
    await wrapper.get('#username').setValue('a')
    await wrapper.get('#password').setValue('b')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))
    expect(wrapper.get('[role=alert]').text()).toBe('Username or password is wrong.')
    expect(wrapper.find('#otp').exists()).toBe(false)
  })

  it('shows the remaining lock time', async () => {
    mockFetch({ 'POST /auth/login': { status: 423, body: {}, headers: { 'Retry-After': '170' } } })
    const { wrapper } = await mountView(LoginView, { route: '/login' })
    await wrapper.get('#username').setValue('a')
    await wrapper.get('#password').setValue('b')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))
    expect(wrapper.get('[role=alert]').text()).toContain('3 minute(s)')
  })

  it('ignores external redirect targets', async () => {
    mockFetch({
      'POST /auth/login': { body: { access_token: 'tok' } },
      'GET /users/me': { body: { username: 'm', roles: [] } },
    })
    const { wrapper, router } = await mountView(LoginView, { route: '/login?next=//evil.example' })
    await wrapper.get('#username').setValue('a')
    await wrapper.get('#password').setValue('b')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(router.currentRoute.value.path).not.toBe('/login'))
    expect(router.currentRoute.value.fullPath).toBe('/')
  })
})

describe('ForgotPasswordView', () => {
  it('shows a neutral confirmation', async () => {
    const fetch = mockFetch({ 'POST /auth/forgot-password': { status: 204 } })
    const { wrapper } = await mountView(ForgotPasswordView)
    await wrapper.get('#email').setValue('a@example.com')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=sent]').exists()).toBe(true))
    expect(fetch.calls[0].body).toEqual({ email: 'a@example.com' })
  })
})

describe('ResetPasswordView', () => {
  it('rejects an invalid link', async () => {
    mockFetch({ 'GET /auth/link-info': { status: 400, body: {} } })
    const { wrapper } = await mountView(ResetPasswordView, { route: '/reset-password?token=bad' })
    expect(wrapper.find('[data-test=invalid]').exists()).toBe(true)
    expect(wrapper.find('form').exists()).toBe(false)
  })

  it('submits the new password with the token', async () => {
    const fetch = mockFetch({
      'GET /auth/link-info': { body: { purpose: 'reset', email: 'a@example.com' } },
      'POST /auth/reset-password': { status: 204 },
    })
    const { wrapper } = await mountView(ResetPasswordView, { route: '/reset-password?token=tok' })
    await wrapper.get('#new-password').setValue('neuespass1')
    await wrapper.get('#repeat-password').setValue('anders123')
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeDefined()
    await wrapper.get('#repeat-password').setValue('neuespass1')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=done]').exists()).toBe(true))
    expect(fetch.calls.at(-1).body).toEqual({ token: 'tok', new_password: 'neuespass1' })
  })
})

describe('HomeView', () => {
  const sprachen = [
    { id: 's-de', sprache2: 'de', sprache_land: 'Deutsch' },
    { id: 's-en', sprache2: 'en', sprache_land: 'English' },
  ]
  const ort = {
    id: 'o1',
    kreis_id: 'k1',
    gov_id: 'PRZYSLKN',
    lat: '49.780000',
    lon: '22.760000',
    namen: [
      { id: 'n1', sprache_id: 's-de', ortsname: 'Przemyśl' },
      { id: 'n2', sprache_id: 's-en', ortsname: 'Przemysl' },
    ],
    karten: [{ id: 'm1', karte: 'Lück', koordinate: 'B5' }],
  }

  function setup(orte) {
    return mockFetch({
      'GET /kreise': { body: [{ id: 'k1', gov_id: 'K', namen: [{ sprache_id: 's-de', kreisname: 'Kreis Przemyśl' }] }] },
      'GET /sprachen': { body: sprachen },
      'GET /orte': { body: orte },
    })
  }

  async function mountHome(orte, language = 'de') {
    setup(orte)
    const pinia = (await import('pinia')).createPinia()
    ;(await import('pinia')).setActivePinia(pinia)
    useSettingsStore().sprachen = sprachen
    return mountView(HomeView, { pinia, language })
  }

  it('searches without authentication and shows results with links', async () => {
    const { wrapper } = await mountHome([ort])
    const row = wrapper.get('[data-test=result]')
    expect(row.text()).toContain('Przemyśl')
    expect(row.text()).toContain('Kreis Przemyśl')
    expect(row.text()).toContain('Lück B5')
    const links = row.findAll('a').map((a) => a.attributes('href'))
    expect(links).toContain('https://gov.genealogy.net/item/show/PRZYSLKN')
    expect(links).toContain('https://etomesto.com/map-ukraine_spezialkarte-uk-750/?y=49.780000&x=22.760000')
  })

  it('shows the name in the interface language and the others as secondary', async () => {
    const { wrapper } = await mountHome([ort], 'en')
    const row = wrapper.get('[data-test=result]')
    expect(row.get('strong').text()).toBe('Przemysl')
    expect(row.text()).toContain('Przemyśl')
  })

  it('sends the search term', async () => {
    const fetch = setup([])
    const { wrapper } = await mountView(HomeView)
    await wrapper.get('#q').setValue('lem')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(fetch.calls.at(-1).url.searchParams.get('q')).toBe('lem'))
    expect(fetch.calls.at(-1).headers.Authorization).toBeUndefined()
  })

  it('sends the token when signed in (needed when search is restricted)', async () => {
    const fetch = setup([])
    setToken('tok')
    await mountView(HomeView)
    expect(fetch.calls.find((c) => c.key === 'GET /orte').headers.Authorization).toBe('Bearer tok')
    expect(fetch.calls.find((c) => c.key === 'GET /sprachen').headers.Authorization).toBe('Bearer tok')
  })

  it('shows a message when nothing is found', async () => {
    const { wrapper } = await mountHome([])
    expect(wrapper.get('[data-test=empty]').text()).toBe('Keine Orte gefunden.')
  })
})
