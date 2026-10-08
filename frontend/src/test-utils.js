import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createGettext } from 'vue3-gettext'
import { createMemoryHistory, createRouter } from 'vue-router'
import { vi } from 'vitest'
import translations from './language/translations.json'

// routes: { 'GET /orte': { body, status, headers } | (url, init) => {...} }
export function mockFetch(routes) {
  const calls = []
  const fn = vi.fn(async (url, init = {}) => {
    const parsed = new URL(url)
    const key = `${init.method ?? 'GET'} ${parsed.pathname}`
    calls.push({ key, url: parsed, body: init.body ? JSON.parse(init.body) : undefined, headers: init.headers })
    let handler = routes[key]
    if (typeof handler === 'function') handler = handler(parsed, init)
    if (!handler) return new Response(JSON.stringify({ detail: `unmocked ${key}` }), { status: 500 })
    const status = handler.status ?? 200
    const body = status === 204 ? null : JSON.stringify(handler.body ?? {})
    return new Response(body, { status, headers: handler.headers })
  })
  vi.stubGlobal('fetch', fn)
  fn.calls = calls
  return fn
}

export function makeRouter() {
  const page = { template: '<div />' }
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: page }],
  })
}

export async function mountView(component, { language = 'en', props, route = '/', pinia = createPinia() } = {}) {
  setActivePinia(pinia)
  const router = makeRouter()
  router.push(route)
  await router.isReady()
  const gettext = createGettext({
    availableLanguages: { de: 'Deutsch', en: 'English' },
    defaultLanguage: language,
    translations,
    silent: true,
  })
  const wrapper = mount(component, { props, global: { plugins: [pinia, gettext, router] } })
  await flushPromises()
  return { wrapper, router, pinia }
}
