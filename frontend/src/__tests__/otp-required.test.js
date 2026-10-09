import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { api, setOtpSetupHandler, setToken } from '../api'
import { createAppRouter } from '../router'
import { useAuthStore } from '../stores/auth'
import { mockFetch, mountView } from '../test-utils'
import AccountView from '../views/AccountView.vue'
import SideNav from '../components/SideNav.vue'

vi.mock('qrcode', () => ({ default: { toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,AAA') } }))

const ADMIN = {
  id: '1',
  username: 'boss',
  email: 'b@example.com',
  first_name: 'Boss',
  last_name: null,
  otp_enabled: false,
  otp_setup_required: true,
  roles: ['admin'],
}

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  setToken(null)
  setOtpSetupHandler(() => {})
  vi.unstubAllGlobals()
})

function signedIn(user) {
  const pinia = createPinia()
  setActivePinia(pinia)
  useAuthStore().user = { ...user }
  return pinia
}

async function go(path) {
  const router = createAppRouter(createMemoryHistory())
  await router.push(path)
  return router.currentRoute.value.path
}

describe('router while OTP setup is required', () => {
  it.each(['/', '/users', '/manage/orte', '/about', '/login', '/privacy'])('redirects %s to the account page', async (path) => {
    useAuthStore().user = { ...ADMIN }
    expect(await go(path)).toBe('/account')
  })

  it('allows the account page itself', async () => {
    useAuthStore().user = { ...ADMIN }
    expect(await go('/account')).toBe('/account')
  })

  it('releases the admin as soon as the setup is done', async () => {
    const auth = useAuthStore()
    auth.user = { ...ADMIN }
    expect(await go('/users')).toBe('/account')
    auth.user = { ...ADMIN, otp_enabled: true, otp_setup_required: false }
    expect(await go('/users')).toBe('/users')
  })

  it('does not restrict admins who already have OTP or normal users', async () => {
    const auth = useAuthStore()
    auth.user = { ...ADMIN, otp_enabled: true, otp_setup_required: false }
    expect(await go('/manage/kreise')).toBe('/manage/kreise')
    auth.user = { ...ADMIN, roles: ['user'], otp_setup_required: false }
    expect(await go('/manage/kreise')).toBe('/manage/kreise')
  })

  it('does not restrict anonymous visitors', async () => {
    expect(await go('/about')).toBe('/about')
  })
})

describe('api', () => {
  it('notifies the app when the server demands the OTP setup', async () => {
    const handler = vi.fn()
    setOtpSetupHandler(handler)
    mockFetch({ 'GET /users': { status: 403, body: { detail: 'otp_setup_required' } } })
    await expect(api('/users')).rejects.toMatchObject({ status: 403 })
    expect(handler).toHaveBeenCalledOnce()
  })

  it('ignores other 403 responses', async () => {
    const handler = vi.fn()
    setOtpSetupHandler(handler)
    mockFetch({ 'GET /users': { status: 403, body: { detail: 'Keine Berechtigung' } } })
    await expect(api('/users')).rejects.toMatchObject({ status: 403 })
    expect(handler).not.toHaveBeenCalled()
  })
})

describe('SideNav while OTP setup is required', () => {
  it('only offers the account page and logout', async () => {
    const { wrapper } = await mountView(SideNav, { pinia: signedIn(ADMIN) })
    const text = wrapper.text()
    expect(text).toContain('My account')
    expect(text).toContain('Log out')
    for (const hidden of ['Search places', 'Management', 'User management', 'Imprint', 'API documentation']) {
      expect(text).not.toContain(hidden)
    }
  })
})

describe('AccountView while OTP setup is required', () => {
  it('shows the notice, the OTP setup form and hides the other sections', async () => {
    mockFetch({})
    const { wrapper } = await mountView(AccountView, { pinia: signedIn(ADMIN) })
    expect(wrapper.get('[data-test=otp-required]').text()).toBe(
      'As an administrator you must set up OTP before you can continue.',
    )
    expect(wrapper.find('#otp-password').exists()).toBe(true)
    expect(wrapper.find('#profile-email').exists()).toBe(false)
    expect(wrapper.find('#current-password').exists()).toBe(false)
  })

  it('is translated to German', async () => {
    mockFetch({})
    const { wrapper } = await mountView(AccountView, { pinia: signedIn(ADMIN), language: 'de' })
    expect(wrapper.get('[data-test=otp-required]').text()).toBe(
      'Als Administrator müssen Sie OTP einrichten, bevor Sie fortfahren können.',
    )
  })

  it('completes the setup and then shows the normal account page', async () => {
    const fetch = mockFetch({
      'POST /users/me/otp/start': { body: { secret: 'ABC', uri: 'otpauth://totp/x?secret=ABC', setup_token: 'st' } },
      'POST /users/me/otp/confirm': { status: 204 },
      'GET /users/me': { body: { ...ADMIN, otp_enabled: true, otp_setup_required: false } },
    })
    const pinia = signedIn(ADMIN)
    const { wrapper } = await mountView(AccountView, { pinia })

    await wrapper.get('#otp-password').setValue('geheim123')
    await wrapper.get('#otp-password').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('#otp-confirm').exists()).toBe(true))
    expect(fetch.calls.find((c) => c.key === 'POST /users/me/otp/start').body).toEqual({
      password: 'geheim123',
      otp: null,
    })

    await wrapper.get('#otp-confirm').setValue('123456')
    await wrapper.get('#otp-confirm').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('[data-test=otp-required]').exists()).toBe(false))
    expect(fetch.calls.find((c) => c.key === 'POST /users/me/otp/confirm').body).toEqual({
      setup_token: 'st',
      code: '123456',
    })
    expect(useAuthStore(pinia).otpSetupRequired).toBe(false)
    expect(wrapper.find('#profile-email').exists()).toBe(true)
    expect(wrapper.get('[data-test=otp-status]').text()).toBe('OTP is enabled.')
  })

  it('keeps the restriction when the code is wrong', async () => {
    mockFetch({
      'POST /users/me/otp/start': { body: { secret: 'ABC', uri: 'otpauth://totp/x?secret=ABC', setup_token: 'st' } },
      'POST /users/me/otp/confirm': { status: 400, body: { detail: 'Code falsch' } },
    })
    const { wrapper } = await mountView(AccountView, { pinia: signedIn(ADMIN) })
    await wrapper.get('#otp-password').setValue('geheim123')
    await wrapper.get('#otp-password').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('#otp-confirm').exists()).toBe(true))
    await wrapper.get('#otp-confirm').setValue('000000')
    await wrapper.get('#otp-confirm').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('[role=alert].alert-danger').exists()).toBe(true))
    expect(wrapper.find('[data-test=otp-required]').exists()).toBe(true)
  })

  it('shows no notice for admins who already use OTP', async () => {
    mockFetch({})
    const user = { ...ADMIN, otp_enabled: true, otp_setup_required: false }
    const { wrapper } = await mountView(AccountView, { pinia: signedIn(user) })
    expect(wrapper.find('[data-test=otp-required]').exists()).toBe(false)
    expect(wrapper.find('#profile-email').exists()).toBe(true)
  })
})
