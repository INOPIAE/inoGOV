import { afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { setToken } from '../api'
import { useAuthStore } from '../stores/auth'
import { mockFetch, mountView } from '../test-utils'
import SetupAccountView from '../views/SetupAccountView.vue'
import AccountView from '../views/AccountView.vue'
import UsersView from '../views/UsersView.vue'

afterEach(() => {
  setToken(null)
  vi.unstubAllGlobals()
})

describe('SetupAccountView', () => {
  function routes(extra = {}) {
    return {
      'GET /auth/link-info': { body: { purpose: 'invite', email: 'neu@example.com', username: null } },
      'POST /auth/setup-account': { body: { access_token: 'tok' } },
      'GET /users/me': { body: { username: 'neuer', roles: ['user'] } },
      ...extra,
    }
  }

  async function fill(wrapper, { first = '', last = '' } = {}) {
    await wrapper.get('#username').setValue('neuer')
    await wrapper.get('#first-name').setValue(first)
    await wrapper.get('#last-name').setValue(last)
    await wrapper.get('#password').setValue('passwort1')
    await wrapper.get('#repeat').setValue('passwort1')
  }

  it('asks the user for first and last name', async () => {
    mockFetch(routes())
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=tok' })
    expect(wrapper.find('#first-name').exists()).toBe(true)
    expect(wrapper.find('#last-name').exists()).toBe(true)
  })

  it('does not allow submitting without any name', async () => {
    const fetch = mockFetch(routes())
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=tok' })
    await fill(wrapper)
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeDefined()
    await wrapper.get('form').trigger('submit')
    expect(fetch.calls.some((c) => c.key === 'POST /auth/setup-account')).toBe(false)
  })

  it('treats whitespace as empty', async () => {
    mockFetch(routes())
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=tok' })
    await fill(wrapper, { first: '   ', last: '  ' })
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeDefined()
  })

  it.each([
    [{ first: 'Ann' }, { first_name: 'Ann', last_name: null }],
    [{ last: 'Muster' }, { first_name: null, last_name: 'Muster' }],
    [{ first: 'Ann', last: 'Muster' }, { first_name: 'Ann', last_name: 'Muster' }],
  ])('sends the names %j', async (input, expected) => {
    const fetch = mockFetch(routes())
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=tok' })
    await fill(wrapper, input)
    expect(wrapper.get('button[type=submit]').attributes('disabled')).toBeUndefined()
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(fetch.calls.some((c) => c.key === 'POST /auth/setup-account')).toBe(true))
    expect(fetch.calls.find((c) => c.key === 'POST /auth/setup-account').body).toEqual({
      token: 'tok',
      username: 'neuer',
      password: 'passwort1',
      ...expected,
    })
  })

  it('moves on to the optional OTP step after registration', async () => {
    mockFetch(routes())
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=tok' })
    await fill(wrapper, { first: 'Ann' })
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('Skip'))
  })

  it('rejects an expired link', async () => {
    mockFetch({ 'GET /auth/link-info': { status: 400, body: {} } })
    const { wrapper } = await mountView(SetupAccountView, { route: '/setup-account?token=old' })
    expect(wrapper.find('[data-test=invalid]').exists()).toBe(true)
    expect(wrapper.find('#first-name').exists()).toBe(false)
  })
})

describe('AccountView profile', () => {
  const USER = {
    id: '1',
    username: 'marcus',
    email: 'm@example.com',
    first_name: 'Marcus',
    last_name: null,
    otp_enabled: false,
    roles: ['user'],
  }

  async function mountAccount(extra = {}) {
    const pinia = createPinia()
    setActivePinia(pinia)
    useAuthStore().user = { ...USER }
    const fetch = mockFetch({ 'PATCH /users/me': { body: { ...USER, ...extra } } })
    const { wrapper } = await mountView(AccountView, { pinia })
    return { wrapper, fetch, pinia }
  }

  it('shows the current data and keeps the username read-only', async () => {
    const { wrapper } = await mountAccount()
    expect(wrapper.get('#profile-first').element.value).toBe('Marcus')
    expect(wrapper.get('#profile-last').element.value).toBe('')
    expect(wrapper.get('#profile-email').element.value).toBe('m@example.com')
    expect(wrapper.get('#profile-username').element.value).toBe('marcus')
    expect(wrapper.get('#profile-username').attributes('readonly')).toBeDefined()
  })

  it('saves names without asking for a password', async () => {
    const { wrapper, fetch, pinia } = await mountAccount({ last_name: 'Mustermann' })
    expect(wrapper.find('[data-test=email-password]').exists()).toBe(false)
    await wrapper.get('#profile-last').setValue('Mustermann')
    await wrapper.get('#profile-first').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('[data-test=profile-saved]').exists()).toBe(true))
    const body = fetch.calls.find((c) => c.key === 'PATCH /users/me').body
    expect(body).toEqual({ first_name: 'Marcus', last_name: 'Mustermann', email: 'm@example.com' })
    expect(useAuthStore(pinia).user.last_name).toBe('Mustermann')
  })

  it('asks for the current password when the email changes and sends it', async () => {
    const { wrapper, fetch } = await mountAccount({ email: 'neu@example.com' })
    await wrapper.get('#profile-email').setValue('neu@example.com')
    expect(wrapper.find('[data-test=email-password]').exists()).toBe(true)
    await wrapper.get('#profile-password').setValue('geheim123')
    await wrapper.get('#profile-first').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(fetch.calls.some((c) => c.key === 'PATCH /users/me')).toBe(true))
    expect(fetch.calls.find((c) => c.key === 'PATCH /users/me').body).toMatchObject({
      email: 'neu@example.com',
      current_password: 'geheim123',
    })
  })

  it('does not require the password when only the letter case of the email differs', async () => {
    const { wrapper } = await mountAccount()
    await wrapper.get('#profile-email').setValue('M@Example.com')
    expect(wrapper.find('[data-test=email-password]').exists()).toBe(false)
  })

  it('does not allow clearing both names', async () => {
    const { wrapper } = await mountAccount()
    await wrapper.get('#profile-first').setValue('')
    expect(wrapper.get('#profile-first').element.closest('form').querySelector('button[type=submit]').disabled).toBe(true)
  })

  it('shows an error when the password is wrong', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    useAuthStore().user = { ...USER }
    mockFetch({ 'PATCH /users/me': { status: 400, body: { detail: 'x' } } })
    const { wrapper } = await mountView(AccountView, { pinia })
    await wrapper.get('#profile-email').setValue('neu@example.com')
    await wrapper.get('#profile-password').setValue('falsch')
    await wrapper.get('#profile-first').element.closest('form').dispatchEvent(new Event('submit'))
    await vi.waitFor(() => expect(wrapper.find('[role=alert]').exists()).toBe(true))
    expect(wrapper.get('[role=alert]').text()).toBe('The current password is wrong.')
    expect(useAuthStore(pinia).user.email).toBe('m@example.com')
  })

  it('is translated to German', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    useAuthStore().user = { ...USER }
    mockFetch({})
    const { wrapper } = await mountView(AccountView, { pinia, language: 'de' })
    expect(wrapper.text()).toContain('Der Benutzername kann nicht geändert werden.')
    expect(wrapper.text()).toContain('Mindestens Vorname oder Nachname')
  })
})

describe('UsersView invitation', () => {
  it('asks only for the email address', async () => {
    const fetch = mockFetch({ 'GET /users': { body: [] }, 'POST /users/invite': { body: {} } })
    const { wrapper } = await mountView(UsersView)
    const form = wrapper.get('section form')
    expect(form.findAll('input')).toHaveLength(1)
    expect(form.find('select').exists()).toBe(false)
    await form.get('input').setValue('neu@example.com')
    await form.trigger('submit')
    await vi.waitFor(() => expect(fetch.calls.some((c) => c.key === 'POST /users/invite')).toBe(true))
    expect(fetch.calls.find((c) => c.key === 'POST /users/invite').body).toEqual({ email: 'neu@example.com' })
    await vi.waitFor(() => expect(wrapper.get('[role=status]').text()).toBe('Invitation sent.'))
  })
})
