import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { setToken } from '../api'
import { createAppRouter } from '../router'
import { useAuthStore } from '../stores/auth'
import { mockFetch, mountView } from '../test-utils'
import ImportsView from '../views/ImportsView.vue'
import SideNav from '../components/SideNav.vue'

const INFO = [{ key: 'ImportLueck', columns: ['place_name_pl', 'district_name_pl', 'coordinate'] }]

const REPORT = {
  key: 'ImportLueck',
  filename: 'lueck.csv',
  total: 4,
  imported: 2,
  failed: 2,
  errors: [
    { line: 3, code: 'empty_place', message: 'Ortsname fehlt', values: ['', 'K', 'B5'] },
    { line: 5, code: 'coordinate_too_long', message: 'x', values: ['Ort', 'K', 'B55'] },
  ],
  created_kreise: [{ id: 'k1', name: 'Nowy Kreis' }],
  archived_as: '20261009-101010_ImportLueck_abc123_lueck.csv',
  archive_failed: false,
}

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

function chooseFile(wrapper, name = 'lueck.csv') {
  const file = new File(['Ort;Kreis;Koordinate\n'], name, { type: 'text/csv' })
  const input = wrapper.get('#import-file')
  Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
  return input.trigger('change').then(() => file)
}

async function run(wrapper) {
  await wrapper.get('form').trigger('submit')
}

async function mountImports(routes, options) {
  const fetch = mockFetch({ 'GET /imports': { body: INFO }, ...routes })
  const mounted = await mountView(ImportsView, options)
  return { fetch, ...mounted }
}

describe('ImportsView', () => {
  it('lists the available imports with a description', async () => {
    const { wrapper } = await mountImports({})
    expect(wrapper.findAll('#import-key option').map((o) => o.text())).toEqual(['ImportLueck'])
    expect(wrapper.get('[data-test=description]').text()).toContain('Polish place name')
    expect(wrapper.get('[data-test=description]').text()).toContain('"Lück"')
  })

  it('cannot start without a file', async () => {
    const { wrapper, fetch } = await mountImports({})
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeDefined()
    await run(wrapper)
    expect(fetch.calls.some((c) => c.key === 'POST /imports/ImportLueck')).toBe(false)
  })

  it('uploads the file as multipart form data with the token', async () => {
    setToken('tok')
    const { wrapper, fetch } = await mountImports({ 'POST /imports/ImportLueck': { body: REPORT } })
    const file = await chooseFile(wrapper)
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeUndefined()
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=report]').exists()).toBe(true))

    const call = fetch.calls.find((c) => c.key === 'POST /imports/ImportLueck')
    expect(call.body).toBeInstanceOf(FormData)
    expect(call.body.get('file').name).toBe(file.name)
    expect(call.headers.Authorization).toBe('Bearer tok')
    expect(call.headers['Content-Type']).toBeUndefined()
  })

  it('shows the summary, created districts, errors and the archive name', async () => {
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: REPORT } })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=report]').exists()).toBe(true))

    expect(wrapper.get('[data-test=summary]').text()).toBe('2 of 4 rows imported, 2 with errors.')
    expect(wrapper.get('[data-test=summary]').classes()).toContain('alert-warning')
    expect(wrapper.get('[data-test=created]').text()).toContain('Nowy Kreis')

    const rows = wrapper.findAll('[data-test=error-row]')
    expect(rows).toHaveLength(2)
    expect(rows[0].text()).toContain('3')
    expect(rows[0].text()).toContain('Place name is missing.')
    expect(rows[0].text()).toContain('; K; B5')
    expect(rows[1].text()).toContain('Coordinate is longer than 2 characters.')
    expect(wrapper.get('[data-test=archived]').text()).toBe(`File archived as ${REPORT.archived_as}.`)
    expect(wrapper.find('[data-test=archive-failed]').exists()).toBe(false)
  })

  it('shows a success state without the error and district sections when all rows are fine', async () => {
    const clean = { ...REPORT, total: 3, imported: 3, failed: 0, errors: [], created_kreise: [] }
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: clean } })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=summary]').exists()).toBe(true))
    expect(wrapper.get('[data-test=summary]').classes()).toContain('alert-success')
    expect(wrapper.find('[data-test=errors]').exists()).toBe(false)
    expect(wrapper.find('[data-test=created]').exists()).toBe(false)
  })

  it('warns when archiving failed', async () => {
    const failed = { ...REPORT, archived_as: null, archive_failed: true }
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: failed } })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=archive-failed]').exists()).toBe(true))
    expect(wrapper.find('[data-test=archived]').exists()).toBe(false)
  })

  it('falls back to the server message for unknown error codes', async () => {
    const odd = { ...REPORT, errors: [{ line: 2, code: 'new_code', message: 'Neue Meldung', values: [] }] }
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: odd } })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=error-row]').exists()).toBe(true))
    expect(wrapper.get('[data-test=error-row]').text()).toContain('Neue Meldung')
  })

  it.each([
    [413, {}, 'The file is too large.'],
    [422, { detail: 'no_polish' }, 'The Polish language is missing in the language table.'],
    [403, {}, 'You are not allowed to do this.'],
    [500, {}, 'Unexpected error.'],
  ])('shows an error for status %s', async (status, body, text) => {
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { status, body } })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=import-error]').exists()).toBe(true))
    expect(wrapper.get('[data-test=import-error]').text()).toBe(text)
    expect(wrapper.find('[data-test=report]').exists()).toBe(false)
  })

  it('blocks a second start while the import is running', async () => {
    let release
    const pending = new Promise((resolve) => (release = resolve))
    const { wrapper, fetch } = await mountImports({
      'POST /imports/ImportLueck': () => pending.then(() => ({ body: REPORT })),
    })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.get('button[type=submit]').text()).toBe('Please wait...'))
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeDefined()
    await run(wrapper)
    expect(fetch.calls.filter((c) => c.key === 'POST /imports/ImportLueck')).toHaveLength(1)
    release()
    await vi.waitFor(() => expect(wrapper.find('[data-test=report]').exists()).toBe(true))
  })

  it('is translated to German', async () => {
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: REPORT } }, { language: 'de' })
    await chooseFile(wrapper)
    await run(wrapper)
    await vi.waitFor(() => expect(wrapper.find('[data-test=report]').exists()).toBe(true))
    expect(wrapper.get('[data-test=summary]').text()).toBe('2 von 4 Zeilen importiert, 2 mit Fehlern.')
    expect(wrapper.findAll('[data-test=error-row]')[0].text()).toContain('Der Ortsname fehlt.')
    expect(wrapper.get('[data-test=created]').text()).toContain('Neu angelegte Kreise')
  })
})

describe('access to the import page', () => {
  async function go(path) {
    const router = createAppRouter(createMemoryHistory())
    await router.push(path)
    return router.currentRoute.value.path
  }

  it('is reserved for admins', async () => {
    const auth = useAuthStore()
    expect(await go('/manage/imports')).toBe('/login')
    auth.user = { username: 'u', roles: ['user'], otp_setup_required: false }
    expect(await go('/manage/imports')).toBe('/')
    auth.user = { username: 'a', roles: ['admin'], otp_setup_required: false }
    expect(await go('/manage/imports')).toBe('/manage/imports')
  })

  async function navText(roles) {
    const pinia = createPinia()
    setActivePinia(pinia)
    useAuthStore().user = { username: 'x', roles }
    return (await mountView(SideNav, { pinia })).wrapper.text()
  }

  it('is listed in the navigation for admins', async () => {
    const text = await navText(['admin'])
    expect(text).toContain('Management')
    expect(text).toContain('Imports')
  })

  it('is not listed in the navigation for normal users', async () => {
    const text = await navText(['user'])
    expect(text).toContain('Management')
    expect(text).toContain('Districts')
    expect(text).not.toContain('Imports')
  })
})
