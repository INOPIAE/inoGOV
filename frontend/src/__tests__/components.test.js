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
import AboutView from '../views/AboutView.vue'
import OrteView from '../views/OrteView.vue'
import ManageOrteView from '../views/ManageOrteView.vue'
import OrteStatisticsView from '../views/OrteStatisticsView.vue'
import GovSuche from '../components/GovSuche.vue'

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
  it('shows the inactivity notice in German', async () => {
    const { wrapper } = await mountView(LoginView, { language: 'de', route: '/login?reason=inactive' })
    expect(wrapper.find('[role=status]').text()).toBe('Sie wurden nach 60 Minuten Inaktivität abgemeldet.')
  })

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

describe('AboutView', () => {
  it('loads localized project content and links to source and license files', async () => {
    let requestedPath = ''
    vi.stubGlobal('fetch', vi.fn(async (url) => {
      requestedPath = new URL(url, window.location.origin).pathname
      return new Response('## Projektüberblick\ninoGOV dokumentiert historische Orte.', { status: 200 })
    }))
    const { wrapper } = await mountView(AboutView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.get('[data-test=about-content]').text()).toContain('Projektüberblick'))

    expect(requestedPath).toBe('/home/about.de.md')
    expect(wrapper.get('h1').text()).toBe('Über inoGOV')
    expect(wrapper.text()).toContain('Projektinformationen')
    expect(wrapper.get('[data-test=about-content]').text()).toContain('inoGOV dokumentiert historische Orte.')
    expect(wrapper.get('[data-test=version]').text()).toBe('0.1.0')
    expect(wrapper.text()).toContain('GNU Affero General Public License')
    expect(wrapper.get('a[href="/legal/LICENSE"]').text()).toBe('Vollständige Lizenz anzeigen')
    expect(wrapper.get('a[href="/legal/THIRD-PARTY-LICENSES.md"]').text()).toBe(
      'Lizenzen der Drittanbieter anzeigen',
    )
    expect(wrapper.get('a[href="https://github.com/INOPIAE/inogov"]').text()).toBe('Quellcode anzeigen')
    expect(wrapper.text()).not.toContain('Copyright')
  })

  it('shows a translated error when the localized project text cannot be loaded', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('', { status: 404 })))
    const { wrapper } = await mountView(AboutView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))

    expect(wrapper.get('[role=alert]').text()).toBe('Der About-Text konnte nicht geladen werden.')
  })
})

describe('GovSuche', () => {
  const govPlace = {
    id: 'object_1',
    position: { lon: 22.5, lat: 49.8, type: 'point' },
    name: [
      { lang: 'pol', value: 'Przemyśl' },
      { lang: 'deu', value: 'Premissel' },
    ],
  }

  it('searches GOV, adds translated names, and emits selected coordinates', async () => {
    const pinia = (await import('pinia')).createPinia()
    useSettingsStore(pinia).sprachen = [
      { id: 'de', sprache_land: 'Deutsch', sprache2: 'de' },
      { id: 'pl', sprache_land: 'Polski', sprache2: 'pl' },
    ]
    const fetch = mockFetch({ 'GET /gov_suche': { body: [govPlace] } })
    const { wrapper } = await mountView(GovSuche, { language: 'de', pinia })

    expect(wrapper.get('h3').text()).toBe('GOV-Ortssuche')
    await wrapper.get('input[type=search]').setValue('  Przemyśl  ')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('object_1'))

    expect(fetch.calls[0].url.searchParams.get('placename')).toBe('Przemyśl')
    expect(wrapper.text()).toContain('Polski · pol')
    expect(wrapper.text()).toContain('Deutsch · deu')

    const addButtons = wrapper.findAll('button.btn-sm')
    await addButtons[1].trigger('click')
    expect(wrapper.emitted('add')).toEqual([[{ sprache_id: 'pl', text: 'Przemyśl' }]])
    await addButtons[0].trigger('click')
    expect(wrapper.emitted('select-place')).toEqual([
      [{ gov_id: 'object_1', lon: 22.5, lat: 49.8 }],
    ])
  })

  it('shows a translated generic error when GOV search fails', async () => {
    mockFetch({ 'GET /gov_suche': { status: 502, body: { detail: 'GOV API unavailable' } } })
    const { wrapper } = await mountView(GovSuche, { language: 'de' })
    await wrapper.get('input[type=search]').setValue('Przemyśl')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))

    expect(wrapper.get('[role=alert]').text()).toBe('Suche fehlgeschlagen.')
  })
})

describe('ManageOrteView', () => {
  it('selects a GOV result and saves its identifier and coordinates', async () => {
    const place = {
      id: 'o1', gov_id: null, kreis_id: null, lat: null, lon: null, addition: null, comment: null,
      coordinates_not_found: false, namen: [{ id: 'n1', sprache_id: 'de', ortsname: 'Przemyśl' }], karten: [],
    }
    const updated = { ...place, gov_id: 'object_1', lat: '49.8', lon: '22.5' }
    const pinia = (await import('pinia')).createPinia()
    useSettingsStore(pinia).sprachen = [{ id: 'de', sprache_land: 'Deutsch', sprache2: 'de' }]
    const fetch = mockFetch({
      'GET /sprachen': { body: [{ id: 'de', sprache_land: 'Deutsch', sprache2: 'de' }] },
      'GET /kreise': { body: [] },
      'GET /orte': { body: [place] },
      'GET /gov_suche': {
        body: [{ id: 'object_1', position: { lon: 22.5, lat: 49.8, type: 'point' }, name: [] }],
      },
      'PATCH /orte/o1': { body: updated },
    })
    const { wrapper } = await mountView(ManageOrteView, { language: 'de', pinia })
    await vi.waitFor(() => expect(wrapper.find('[data-test=list-item]').exists()).toBe(true))
    await wrapper.get('[data-test=list-item]').trigger('click')

    const govSearch = wrapper.findComponent(GovSuche)
    await govSearch.get('input[type=search]').setValue('Przemyśl')
    await govSearch.get('form').trigger('submit')
    await vi.waitFor(() => expect(govSearch.text()).toContain('object_1'))
    await govSearch.get('button.btn-sm').trigger('click')
    await vi.waitFor(() => expect(wrapper.find('[role=status]').text()).toBe('Gespeichert.'))

    const patch = fetch.calls.find((call) => call.key === 'PATCH /orte/o1')
    expect(patch.body).toMatchObject({ gov_id: 'object_1', lat: 49.8, lon: 22.5 })
  })
})

describe('OrteStatisticsView', () => {
  it('shows translated statistics and refreshes them on request', async () => {
    const fetch = mockFetch({
      'GET /orte/statistics/': { body: { total: 10, gov: 3, geo: 5, not_found: 2 } },
    })
    const { wrapper } = await mountView(OrteStatisticsView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.find('button').text()).toBe('Aktualisieren'))

    expect(wrapper.text()).toContain('Ortsstatistik')
    expect(wrapper.text()).toContain('Orte mit GOV-ID')
    expect(wrapper.text()).toContain('Orte mit Koordinaten')
    expect(wrapper.text()).toContain('Orte mit Koordinaten nicht gefunden')
    expect(wrapper.findAll('.card').map((card) => card.text())).toEqual([
      'Orte10',
      'Orte mit GOV-ID330 %',
      'Orte mit Koordinaten550 %',
      'Orte mit Koordinaten nicht gefunden220 %',
    ])

    await wrapper.get('button').trigger('click')
    await vi.waitFor(() => expect(fetch.calls.filter((call) => call.key === 'GET /orte/statistics/')).toHaveLength(2))
  })

  it('does not render percentages when there are no places', async () => {
    mockFetch({
      'GET /orte/statistics/': { body: { total: 0, gov: 0, geo: 0, not_found: 0 } },
    })
    const { wrapper } = await mountView(OrteStatisticsView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.findAll('.card')).toHaveLength(4))

    expect(wrapper.findAll('.card').map((card) => card.text())).toEqual([
      'Orte0',
      'Orte mit GOV-ID0',
      'Orte mit Koordinaten0',
      'Orte mit Koordinaten nicht gefunden0',
    ])
    expect(wrapper.text()).not.toContain('%')
  })

  it('shows a translated error when loading statistics fails', async () => {
    mockFetch({ 'GET /orte/statistics/': { status: 500, body: {} } })
    const { wrapper } = await mountView(OrteStatisticsView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))

    expect(wrapper.get('[role=alert]').text()).toBe('Unerwarteter Fehler.')
  })
})

describe('HomeView', () => {
  it('loads the German welcome text and routes the search term to places', async () => {
    let requestedPath = ''
    vi.stubGlobal('fetch', vi.fn(async (url) => {
      requestedPath = new URL(url, window.location.origin).pathname
      return new Response('## Willkommen in inoGOV', { status: 200 })
    }))

    const { wrapper, router } = await mountView(HomeView, { language: 'de' })
    await vi.waitFor(() => expect(wrapper.get('[data-test=welcome-content]').text()).toContain('Willkommen in inoGOV'))
    expect(requestedPath).toBe('/home/welcome.de.md')
    expect(wrapper.get('h1').text()).toBe('Willkommen auf inoGov')

    await wrapper.get('#home-place-search').setValue('Lviv')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(router.currentRoute.value.query.q).toBe('Lviv'))
    expect(router.currentRoute.value.path).toBe('/orte')
  })

  it('hides the search form when public search is disabled', async () => {
    const { createPinia, setActivePinia } = await import('pinia')
    const pinia = createPinia()
    setActivePinia(pinia)
    useSettingsStore().publicSearch = false
    vi.stubGlobal('fetch', vi.fn(async () => new Response('Welcome', { status: 200 })))

    const { wrapper } = await mountView(HomeView, { pinia })

    expect(wrapper.find('form').exists()).toBe(false)
  })
})

describe('OrteView', () => {
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

  function setup(orte, total = orte.length) {
    return mockFetch({
      'GET /kreise': { body: [{ id: 'k1', gov_id: 'K', namen: [{ sprache_id: 's-de', kreisname: 'Kreis Przemyśl' }] }] },
      'GET /sprachen': { body: sprachen },
      'GET /orte': { body: orte },
      'GET /orte/count': { body: { found: orte.length, total } },
    })
  }

  async function mountHome(orte, language = 'de', total = orte.length) {
    const fetch = setup(orte, total)
    const pinia = (await import('pinia')).createPinia()
    ;(await import('pinia')).setActivePinia(pinia)
    useSettingsStore().sprachen = sprachen
    return { ...(await mountView(OrteView, { pinia, language })), fetch }
  }

  it('searches without authentication and shows results with links', async () => {
    const { wrapper } = await mountHome([ort])
    expect(wrapper.find('#coordinate-status').exists()).toBe(false)
    expect(wrapper.find('#link-status').exists()).toBe(false)
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
    const { wrapper } = await mountView(OrteView)
    await wrapper.get('#q').setValue('lem')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(fetch.calls.at(-1).url.searchParams.get('q')).toBe('lem'))
    expect(fetch.calls.at(-1).headers.Authorization).toBeUndefined()
  })

  it('uses a search term passed in the route query', async () => {
    const fetch = setup([])
    await mountView(OrteView, { route: '/orte?q=Przemysl' })
    await vi.waitFor(() =>
      expect(fetch.calls.find((call) => call.key === 'GET /orte').url.searchParams.get('q')).toBe('Przemysl'),
    )
  })

  it('sends the token when signed in (needed when search is restricted)', async () => {
    const fetch = setup([])
    setToken('tok')
    await mountView(OrteView)
    expect(fetch.calls.find((c) => c.key === 'GET /orte').headers.Authorization).toBe('Bearer tok')
    expect(fetch.calls.find((c) => c.key === 'GET /sprachen').headers.Authorization).toBe('Bearer tok')
  })

  it('shows a message when nothing is found', async () => {
    const { wrapper } = await mountHome([])
    expect(wrapper.get('[data-test=empty]').text()).toBe('Keine Orte gefunden.')
  })

  it('sorts by name by default and sends new sort choices to the server', async () => {
    const place = (id, name) => ({
      ...ort,
      id,
      namen: [{ id: `name-${id}`, sprache_id: 's-de', ortsname: name }],
    })
    const { wrapper, fetch } = await mountHome([place('z', 'Zamość'), place('a', 'Alwernia')])
    const placeRequests = () => fetch.calls.filter((call) => call.key === 'GET /orte')

    expect(wrapper.get('th[aria-sort=ascending] [data-sort=name]').exists()).toBe(true)
    expect(placeRequests()[0].url.searchParams.get('sort_by')).toBe('name')
    expect(placeRequests()[0].url.searchParams.get('sort_order')).toBe('asc')
    expect(placeRequests()[0].url.searchParams.get('sort_sprache_id')).toBe('s-de')

    await wrapper.get('[data-sort=name]').trigger('click')
    await vi.waitFor(() => expect(placeRequests().at(-1).url.searchParams.get('sort_order')).toBe('desc'))

    expect(wrapper.get('th[aria-sort=descending] [data-sort=name]').exists()).toBe(true)
    expect(wrapper.findAll('thead [data-sort]').map((button) => button.attributes('data-sort'))).toEqual([
      'name',
      'district',
      'coordinates',
      'maps',
      'links',
    ])
    expect(wrapper.findAll('thead [data-sort]').map((button) => button.attributes('title'))).toEqual(
      Array(5).fill('Zum Sortieren nach dieser Spalte anklicken.'),
    )
  })

  it('shows filtered result count and global total below the results', async () => {
    const { wrapper } = await mountHome([ort], 'de', 12)
    expect(wrapper.get('[data-test=result-count]').text()).toBe('1 von 12 Orten gefunden.')
  })

  it('shows translated filters to signed-in users and applies them to results and counts', async () => {
    const pinia = await signedIn(['user'])
    const fetch = setup([ort], 12)
    const { wrapper } = await mountView(OrteView, { pinia, language: 'de' })

    expect(wrapper.get('label[for=coordinate-status]').text()).toBe('Koordinaten filtern')
    expect(wrapper.get('label[for=link-status]').text()).toBe('Links filtern')

    await wrapper.get('#coordinate-status').setValue('not_found')
    await vi.waitFor(() => {
      const request = fetch.calls.filter((call) => call.key === 'GET /orte').at(-1)
      expect(request.url.searchParams.get('coordinate_status')).toBe('not_found')
    })
    await vi.waitFor(() => expect(wrapper.get('#link-status').attributes('disabled')).toBeUndefined())

    await wrapper.get('#link-status').setValue('without_gov')
    await vi.waitFor(() => {
      const listRequest = fetch.calls.filter((call) => call.key === 'GET /orte').at(-1)
      const countRequest = fetch.calls.filter((call) => call.key === 'GET /orte/count').at(-1)
      expect(listRequest.url.searchParams.get('link_status')).toBe('without_gov')
      expect(countRequest.url.searchParams.get('coordinate_status')).toBe('not_found')
      expect(countRequest.url.searchParams.get('link_status')).toBe('without_gov')
    })
  })
})
