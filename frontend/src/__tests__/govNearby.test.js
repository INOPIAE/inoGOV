import { afterEach, describe, expect, it, vi } from 'vitest'
import { mockFetch, mountView } from '../test-utils'
import GovNearbyView from '../views/GovNearbyView.vue'
import ManageOrteView from '../views/ManageOrteView.vue'

afterEach(() => vi.unstubAllGlobals())

const result = {
  id: 'LAWROWKO20OP',
  position: { lon: 25.2099, lat: 50.6257, type: 'p' },
  name: [{ lang: 'deu', value: 'Lawriw' }],
}

const place = {
  id: 'o1', gov_id: 'GOV1', kreis_id: null, lat: 50.73, lon: 25.21, addition: null, comment: null,
  coordinates_not_found: false, namen: [], karten: [], regional_maps: [],
}

describe('GovNearbyView', () => {
  it('prefills the search area from the place coordinates without showing the id', async () => {
    mockFetch({})
    const { wrapper } = await mountView(GovNearbyView, { route: '/gov-nearby?ort_id=o1&lat=50.730346&lon=25.2' })

    expect(wrapper.get('#nearby-latitude0').element.value).toBe('50.7')
    expect(wrapper.get('#nearby-latitude1').element.value).toBe('50.8')
    expect(wrapper.get('#nearby-longitude0').element.value).toBe('25.15')
    expect(wrapper.get('#nearby-longitude1').element.value).toBe('25.25')
    expect(wrapper.text()).not.toContain('o1')
    expect(wrapper.find('[data-test=current-gov-id]').exists()).toBe(false)
  })

  it('shows the GOV id of the calling place', async () => {
    mockFetch({})
    const { wrapper } = await mountView(GovNearbyView, { route: '/gov-nearby?ort_id=o1&gov_id=GOV1' })

    expect(wrapper.get('[data-test=current-gov-id]').text()).toContain('GOV1')
    expect(wrapper.text()).not.toContain('o1')
  })

  it('labels the search area fields', async () => {
    mockFetch({})
    const { wrapper } = await mountView(GovNearbyView, { language: 'de', route: '/gov-nearby' })

    expect(wrapper.get('label[for=nearby-latitude0]').text()).toBe('Breite Start')
    expect(wrapper.get('label[for=nearby-latitude1]').text()).toBe('Breite Ende')
    expect(wrapper.get('label[for=nearby-longitude0]').text()).toBe('Länge Start')
    expect(wrapper.get('label[for=nearby-longitude1]').text()).toBe('Länge Ende')
  })

  it('returns to place management with the selected result', async () => {
    const fetch = mockFetch({ 'GET /gov_suche_nearby': { body: [result] } })
    const { wrapper, router } = await mountView(GovNearbyView, { route: '/gov-nearby?ort_id=o1&lat=50.6&lon=25.2' })

    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=select-result]').exists()).toBe(true))
    expect(fetch.calls.some((c) => c.key === 'GET /gov_suche_nearby')).toBe(true)

    await wrapper.get('[data-test=select-result]').trigger('click')
    await vi.waitFor(() => expect(router.currentRoute.value.fullPath).toBe('/manage/orte?ort_id=o1'))
  })

  it('offers no selection without a calling place', async () => {
    mockFetch({ 'GET /gov_suche_nearby': { body: [result] } })
    const { wrapper } = await mountView(GovNearbyView, { route: '/gov-nearby' })
    await wrapper.get('#nearby-latitude').setValue('50.6')
    await wrapper.get('#nearby-longitude').setValue('25.2')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('[data-test=nearby-result]').exists()).toBe(true))

    expect(wrapper.find('[data-test=select-result]').exists()).toBe(false)
  })
})

describe('ManageOrteView GOV nearby', () => {
  it('links to the nearby search with id, coordinates and GOV id', async () => {
    mockFetch({
      'GET /sprachen': { body: [] },
      'GET /kreise': { body: [] },
      'GET /orte': { body: [place] },
      'GET /orte/o1': { body: place },
    })
    const { wrapper } = await mountView(ManageOrteView, { route: '/manage/orte?ort_id=o1' })

    const href = wrapper.get('[data-test=gov-nearby]').attributes('href')
    expect(href).toBe('/gov-nearby?ort_id=o1&lat=50.73&lon=25.21&gov_id=GOV1')
  })

  it('shows the selected GOV data above the GOV search', async () => {
    mockFetch({
      'GET /sprachen': { body: [] },
      'GET /kreise': { body: [] },
      'GET /orte': { body: [place] },
      'GET /orte/o1': { body: place },
    })
    const { wrapper, pinia } = await mountView(ManageOrteView, { route: '/manage/orte?ort_id=o1' })
    expect(wrapper.find('[data-test=gov-selection]').exists()).toBe(false)

    const { useGovSelectionStore } = await import('../stores/govSelection')
    useGovSelectionStore(pinia).select('o1', result)
    await vi.waitFor(() => expect(wrapper.find('[data-test=gov-selection]').exists()).toBe(true))

    const text = wrapper.get('[data-test=gov-selection]').text()
    expect(text).toContain('LAWROWKO20OP')
    expect(text).toContain('50.6257, 25.2099')
    expect(text).toContain('Lawriw')
  })
})
