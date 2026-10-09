import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { setToken } from '../api'
import { createAppRouter } from '../router'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { mockFetch, mountView } from '../test-utils'
import MapView from '../views/MapView.vue'
import HomeView from '../views/HomeView.vue'
import ImportsView from '../views/ImportsView.vue'

const SQUARE = {
  karte: 'Lück',
  koordinate: 'B1',
  image: { filename: 'Lueck1927_gr.jpg', width_px: 2000, height_px: 1362 },
  area: { x1: 357, y1: 35, x2: 677, y2: 248 },
  extent: { lon_from: 42.5, lon_to: 43, lat_from: 51, lat_to: 50 },
}
const URL_PATH = 'GET /maps/L%C3%BCck/B1'
const ROUTE = '/map/L%C3%BCck/B1'

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

async function mountMap(routes = { [URL_PATH]: { body: SQUARE } }, options = {}) {
  const fetch = mockFetch(routes)
  const mounted = await mountView(MapView, { route: ROUTE, ...options })
  return { fetch, ...mounted }
}

function size(wrapper, width, height) {
  const el = wrapper.get('[data-test=viewport]').element
  Object.defineProperty(el, 'clientWidth', { value: width, configurable: true })
  Object.defineProperty(el, 'clientHeight', { value: height, configurable: true })
  return el
}

const canvasWidth = (wrapper) => parseFloat(wrapper.get('[data-test=canvas]').element.style.width)
const percent = (wrapper) => wrapper.get('[data-test=percent]').text()

describe('MapView', () => {
  it('requests the square by map and coordinate', async () => {
    const { fetch } = await mountMap()
    expect(fetch.calls[0].key).toBe(URL_PATH)
  })

  it('shows title, extent and the image from the configured maps folder', async () => {
    const { wrapper } = await mountMap()
    expect(wrapper.get('[data-test=title]').text()).toBe('Map "Lück", square B1')
    expect(wrapper.get('[data-test=extent]').text()).toBe('Longitude 42.5 to 43, latitude 51 to 50')
    const img = wrapper.get('img')
    expect(img.attributes('src')).toBe('/maps/Lueck1927_gr.jpg')
    expect(img.attributes('alt')).toBe('Map image with the highlighted square B1')
  })

  it('starts at 100 % with the image in its natural size', async () => {
    const { wrapper } = await mountMap()
    expect(percent(wrapper)).toBe('Zoom: 100 %')
    expect(canvasWidth(wrapper)).toBe(2000)
    expect(parseFloat(wrapper.get('[data-test=canvas]').element.style.height)).toBe(1362)
  })

  it('highlights the square with percentages of the image size', async () => {
    const { wrapper } = await mountMap()
    const style = wrapper.get('[data-test=highlight]').element.style
    expect(parseFloat(style.left)).toBeCloseTo((357 / 2000) * 100, 4)
    expect(parseFloat(style.top)).toBeCloseTo((35 / 1362) * 100, 4)
    expect(parseFloat(style.width)).toBeCloseTo(16, 4)
    expect(parseFloat(style.height)).toBeCloseTo((213 / 1362) * 100, 4)
  })

  it('keeps the highlight on the same spot when zooming (relative sizes)', async () => {
    const { wrapper } = await mountMap()
    const before = wrapper.get('[data-test=highlight]').attributes('style')
    await wrapper.get('[data-test=zoom-in]').trigger('click')
    expect(wrapper.get('[data-test=highlight]').attributes('style')).toBe(before)
  })

  it('zooms in and out in steps and shows the percentage', async () => {
    const { wrapper } = await mountMap()
    size(wrapper, 400, 300)
    await wrapper.get('[data-test=zoom-in]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 125 %')
    expect(canvasWidth(wrapper)).toBe(2500)
    await wrapper.get('[data-test=zoom-out]').trigger('click')
    await wrapper.get('[data-test=zoom-out]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 80 %')
    expect(canvasWidth(wrapper)).toBe(1600)
  })

  it('limits the zoom range', async () => {
    const { wrapper } = await mountMap()
    size(wrapper, 400, 300)
    for (let i = 0; i < 30; i++) await wrapper.get('[data-test=zoom-in]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 400 %')
    for (let i = 0; i < 40; i++) await wrapper.get('[data-test=zoom-out]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 10 %')
  })

  it('zooms with ctrl + mouse wheel but lets the plain wheel scroll', async () => {
    const { wrapper } = await mountMap()
    size(wrapper, 400, 300)
    const viewport = wrapper.get('[data-test=viewport]')
    const wheel = async (deltaY, ctrlKey) => {
      const event = new WheelEvent('wheel', { deltaY, ctrlKey, bubbles: true, cancelable: true })
      viewport.element.dispatchEvent(event)
      await wrapper.vm.$nextTick()
      return event
    }
    expect((await wheel(-100, false)).defaultPrevented).toBe(false)
    expect(percent(wrapper)).toBe('Zoom: 100 %')
    expect((await wheel(-100, true)).defaultPrevented).toBe(true)
    expect(percent(wrapper)).toBe('Zoom: 125 %')
    await wheel(100, true)
    expect(percent(wrapper)).toBe('Zoom: 100 %')
  })

  it('fits the image to the width of the view', async () => {
    const { wrapper } = await mountMap()
    size(wrapper, 500, 300)
    await wrapper.get('[data-test=fit]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 25 %')
    expect(canvasWidth(wrapper)).toBe(500)
  })

  it('returns to the actual size and centres the square', async () => {
    const { wrapper } = await mountMap()
    const view = size(wrapper, 400, 300)
    await wrapper.get('[data-test=fit]').trigger('click')
    await wrapper.get('[data-test=actual]').trigger('click')
    expect(percent(wrapper)).toBe('Zoom: 100 %')
    expect(view.scrollLeft).toBe((357 + 677) / 2 - 200)
  })

  it('keeps the centre of the view while zooming', async () => {
    const { wrapper } = await mountMap()
    const view = size(wrapper, 400, 300)
    view.scrollLeft = 600
    view.scrollTop = 100
    await wrapper.get('[data-test=zoom-in]').trigger('click')
    // Mitte im Bild: (600 + 200) / 1 = 800 -> nach dem Zoom 800 * 1.25 - 200
    expect(view.scrollLeft).toBe(800 * 1.25 - 200)
    expect(view.scrollTop).toBe(250 * 1.25 - 150)
  })

  it('is scrollable and reachable by keyboard', async () => {
    const { wrapper } = await mountMap()
    const viewport = wrapper.get('[data-test=viewport]')
    expect(viewport.attributes('tabindex')).toBe('0')
    expect(viewport.attributes('role')).toBe('region')
    expect(viewport.attributes('aria-label')).toBe('Map view')
  })

  it('tells the user when the image file is missing', async () => {
    const { wrapper } = await mountMap()
    expect(wrapper.find('[data-test=image-failed]').exists()).toBe(false)
    await wrapper.get('img').trigger('error')
    expect(wrapper.get('[data-test=image-failed]').text()).toBe('The map image could not be loaded.')
  })

  it('shows a message when no data exists for the square', async () => {
    const { wrapper } = await mountMap({ [URL_PATH]: { status: 404, body: {} } })
    expect(wrapper.get('[data-test=missing]').text()).toBe('No map data is available for this square.')
    expect(wrapper.find('[data-test=viewport]').exists()).toBe(false)
  })

  it('shows an error for other failures', async () => {
    const { wrapper } = await mountMap({ [URL_PATH]: { status: 500, body: {} } })
    expect(wrapper.get('[data-test=error]').text()).toBe('Unexpected error.')
  })

  it('sends the token when signed in (restricted search)', async () => {
    setToken('tok')
    const { fetch } = await mountMap()
    expect(fetch.calls[0].headers.Authorization).toBe('Bearer tok')
  })

  it('is translated to German', async () => {
    const { wrapper } = await mountMap(undefined, { language: 'de' })
    expect(wrapper.get('[data-test=title]').text()).toBe('Karte „Lück“, Planquadrat B1')
    expect(percent(wrapper)).toBe('Zoom: 100 %')
    expect(wrapper.get('[data-test=fit]').text()).toBe('An Breite anpassen')
    expect(wrapper.get('[data-test=extent]').text()).toBe('Längengrad 42.5 bis 43, Breitengrad 51 bis 50')
  })
})

describe('map page access', () => {
  async function go(path) {
    const router = createAppRouter(createMemoryHistory())
    await router.push(path)
    return router.currentRoute.value
  }

  it('is public when the search is public', async () => {
    useSettingsStore().publicSearch = true
    const route = await go(ROUTE)
    expect(route.name).toBe('map')
    expect(route.params).toEqual({ karte: 'Lück', koordinate: 'B1' })
  })

  it('requires a login when the search is restricted', async () => {
    useSettingsStore().publicSearch = false
    const route = await go(ROUTE)
    expect(route.path).toBe('/login')
    expect(route.query.next).toBe(ROUTE)
    useAuthStore().user = { username: 'u', roles: ['user'] }
    expect((await go(ROUTE)).name).toBe('map')
  })
})

describe('search results link to the map', () => {
  it('opens the map page in a new tab for every map reference', async () => {
    mockFetch({
      'GET /kreise': { body: [] },
      'GET /sprachen': { body: [{ id: 's', sprache2: 'de' }] },
      'GET /orte': {
        body: [
          {
            id: 'o1',
            kreis_id: null,
            gov_id: null,
            lat: null,
            lon: null,
            namen: [{ id: 'n', sprache_id: 's', ortsname: 'Krasiczyn' }],
            karten: [
              { id: 'm1', karte: 'Lück', koordinate: 'B5' },
              { id: 'm2', karte: 'Stumpf', koordinate: null },
            ],
          },
        ],
      },
    })
    const { wrapper } = await mountView(HomeView)
    const links = wrapper.findAll('[data-test=map-link]')
    expect(links).toHaveLength(1)
    expect(links[0].text()).toBe('Lück B5')
    expect(links[0].attributes('href')).toBe('/map/L%C3%BCck/B5')
    expect(links[0].attributes('target')).toBe('_blank')
    expect(links[0].attributes('rel')).toBe('noopener')
    expect(wrapper.get('[data-test=result]').text()).toContain('Stumpf')
  })
})

describe('ImportsView for the coordinate import', () => {
  const INFOS = [
    { key: 'ImportLueck', columns: [], accepts: ['.csv'] },
    { key: 'ImportLueckKoordinaten', columns: [], accepts: ['.xlsx', '.csv'] },
  ]

  async function mountImports(routes = {}, options = {}) {
    const fetch = mockFetch({ 'GET /imports': { body: INFOS }, ...routes })
    const mounted = await mountView(ImportsView, options)
    return { fetch, ...mounted }
  }

  async function choose(wrapper) {
    const file = new File(['x'], 'k.xlsx')
    const input = wrapper.get('#import-file')
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
  }

  it('offers both imports and adapts the accepted file types', async () => {
    const { wrapper } = await mountImports()
    expect(wrapper.get('#import-file').attributes('accept')).toBe('.csv')
    await wrapper.get('#import-key').setValue('ImportLueckKoordinaten')
    expect(wrapper.get('#import-file').attributes('accept')).toBe('.xlsx,.csv')
    expect(wrapper.get('[data-test=description]').text()).toContain('Excel or CSV file')
    expect(wrapper.get('[data-test=description]').text()).toContain('Bildbreite_px')
  })

  it('uploads to the selected import', async () => {
    const report = { key: 'ImportLueckKoordinaten', total: 1, imported: 1, failed: 0, errors: [], created_kreise: [], archived_as: 'a', archive_failed: false }
    const { wrapper, fetch } = await mountImports({ 'POST /imports/ImportLueckKoordinaten': { body: report } })
    await wrapper.get('#import-key').setValue('ImportLueckKoordinaten')
    await choose(wrapper)
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=summary]').exists()).toBe(true))
    expect(fetch.calls.some((c) => c.key === 'POST /imports/ImportLueckKoordinaten')).toBe(true)
  })

  it.each([
    ['no_header', 'The header row with "Koordinate" was not found.'],
    ['no_image_size', 'Bildbreite_px / Bildhoehe_px are missing or invalid.'],
    ['missing_columns', 'Required columns are missing.'],
    ['unreadable', 'The file cannot be read.'],
    ['no_polish', 'The Polish language is missing in the language table.'],
  ])('explains the abort reason %s', async (detail, text) => {
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { status: 422, body: { detail } } })
    await choose(wrapper)
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=import-error]').exists()).toBe(true))
    expect(wrapper.get('[data-test=import-error]').text()).toBe(text)
  })

  it('shows a generic message for an unknown 422 detail', async () => {
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { status: 422, body: { detail: 'neu' } } })
    await choose(wrapper)
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=import-error]').exists()).toBe(true))
    expect(wrapper.get('[data-test=import-error]').text()).toBe('Invalid input.')
  })

  it.each([
    ['bad_number', 'A number is invalid or missing.'],
    ['invalid_area', 'The area is empty or reversed (X2/Y2 must be greater than X1/Y1).'],
    ['outside_image', 'The area lies outside the image.'],
    ['empty_coordinate', 'Coordinate is missing.'],
  ])('translates the row error %s', async (code, text) => {
    const report = {
      key: 'ImportLueck', total: 1, imported: 0, failed: 1, created_kreise: [], archived_as: 'a', archive_failed: false,
      errors: [{ line: 7, code, message: 'x', values: ['A1', '5'] }],
    }
    const { wrapper } = await mountImports({ 'POST /imports/ImportLueck': { body: report } })
    await choose(wrapper)
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=error-row]').exists()).toBe(true))
    expect(wrapper.get('[data-test=error-row]').text()).toContain(text)
  })
})
