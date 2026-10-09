import { afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { setToken } from '../api'
import { useAuthStore } from '../stores/auth'
import { mockFetch, mountView } from '../test-utils'
import AccountView from '../views/AccountView.vue'

afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

async function mountAccount(roles, otpEnabled, language = 'en') {
  const pinia = createPinia()
  setActivePinia(pinia)
  useAuthStore().user = { id: '1', username: 'm', email: 'm@example.com', first_name: 'M', last_name: null, otp_enabled: otpEnabled, roles }
  mockFetch({})
  return (await mountView(AccountView, { pinia, language })).wrapper
}

const buttons = (wrapper) => wrapper.findAll('button').map((b) => b.text())

describe('OTP section for admins', () => {
  it('offers reset but not disable and explains why', async () => {
    const wrapper = await mountAccount(['admin'], true)
    expect(buttons(wrapper)).toContain('Reset OTP')
    expect(buttons(wrapper)).not.toContain('Disable OTP')
    expect(wrapper.get('[data-test=admin-otp-hint]').text()).toBe('Administrators cannot disable OTP.')
  })

  it('treats a user with both roles as admin', async () => {
    const wrapper = await mountAccount(['admin', 'user'], true)
    expect(buttons(wrapper)).not.toContain('Disable OTP')
  })

  it('still lets an admin without OTP set it up, without a hint', async () => {
    const wrapper = await mountAccount(['admin'], false)
    expect(buttons(wrapper)).toContain('Set up OTP')
    expect(wrapper.find('[data-test=admin-otp-hint]').exists()).toBe(false)
  })

  it('keeps disable for normal users', async () => {
    const wrapper = await mountAccount(['user'], true)
    expect(buttons(wrapper)).toContain('Disable OTP')
    expect(buttons(wrapper)).toContain('Reset OTP')
    expect(wrapper.find('[data-test=admin-otp-hint]').exists()).toBe(false)
  })

  it('translates the hint', async () => {
    const wrapper = await mountAccount(['admin'], true, 'de')
    expect(wrapper.get('[data-test=admin-otp-hint]').text()).toBe('Administratoren können OTP nicht deaktivieren.')
  })
})
