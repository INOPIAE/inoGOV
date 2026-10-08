<script setup>
import { computed, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { UI_LANGUAGES, setLanguage } from '../i18n'
import { useAuthStore } from '../stores/auth'
import { useErrors } from '../composables/useErrors'
import OtpSetup from '../components/OtpSetup.vue'

const gettext = useGettext()
const { $gettext } = gettext
const { errorText } = useErrors()
const auth = useAuthStore()

// Profil
const profile = ref({
  first_name: auth.user.first_name ?? '',
  last_name: auth.user.last_name ?? '',
  email: auth.user.email,
  current_password: '',
})
const profileMessage = ref('')
const profileError = ref('')
const emailChanged = computed(() => profile.value.email.trim().toLowerCase() !== auth.user.email.toLowerCase())
const hasName = computed(() => !!(profile.value.first_name.trim() || profile.value.last_name.trim()))

async function saveProfile() {
  if (!hasName.value) return
  profileMessage.value = profileError.value = ''
  const body = {
    first_name: profile.value.first_name.trim(),
    last_name: profile.value.last_name.trim(),
    email: profile.value.email.trim(),
  }
  if (emailChanged.value) body.current_password = profile.value.current_password
  try {
    auth.user = await api('/users/me', { method: 'PATCH', body })
    profile.value.current_password = ''
    profileMessage.value = $gettext('Your profile has been saved.')
  } catch (e) {
    profileError.value = e?.status === 400 ? $gettext('The current password is wrong.') : errorText(e)
  }
}

// Passwort ändern
const pw = ref({ current: '', next: '', repeat: '' })
const pwMessage = ref('')
const pwError = ref('')

async function changePassword() {
  pwMessage.value = pwError.value = ''
  try {
    await api('/users/me/password', {
      method: 'PUT',
      body: { current_password: pw.value.current, new_password: pw.value.next },
    })
    pwMessage.value = $gettext('Your password has been changed.')
    pw.value = { current: '', next: '', repeat: '' }
  } catch (e) {
    pwError.value = e?.status === 400 ? $gettext('The current password is wrong.') : errorText(e)
  }
}

// OTP: mode = null | 'enable' | 'disable', stage = 'form' | 'setup'
const mode = ref(null)
const stage = ref('form')
const otpForm = ref({ password: '', otp: '' })
const otpError = ref('')
const otpMessage = ref('')

function openOtp(newMode) {
  mode.value = newMode
  stage.value = 'form'
  otpForm.value = { password: '', otp: '' }
  otpError.value = otpMessage.value = ''
}

const credentials = () => ({ password: otpForm.value.password, otp: otpForm.value.otp || null })

async function submitOtpForm() {
  otpError.value = ''
  if (mode.value === 'enable') {
    stage.value = 'setup'
    return
  }
  try {
    await api('/users/me/otp/disable', { method: 'POST', body: credentials() })
    await auth.fetchMe()
    mode.value = null
    otpMessage.value = $gettext('OTP has been disabled.')
  } catch (e) {
    otpError.value = e?.status === 400 ? $gettext('Password or code is wrong.') : errorText(e)
  }
}

const startOtp = () => api('/users/me/otp/start', { method: 'POST', body: credentials() })
const confirmOtp = (setupToken, code) =>
  api('/users/me/otp/confirm', { method: 'POST', body: { setup_token: setupToken, code } })

async function otpDone() {
  await auth.fetchMe()
  mode.value = null
  otpMessage.value = $gettext('OTP has been set up.')
}
</script>

<template>
  <div class="col-12 col-lg-8">
    <h1 class="h3 mb-3">{{ $gettext('My account') }}</h1>

    <section class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('Profile') }}</h2>
        <div v-if="profileMessage" class="alert alert-success" role="status" data-test="profile-saved">{{ profileMessage }}</div>
        <div v-if="profileError" class="alert alert-danger" role="alert">{{ profileError }}</div>
        <form @submit.prevent="saveProfile">
          <div class="mb-3">
            <label class="form-label" for="profile-username">{{ $gettext('Username') }}</label>
            <input id="profile-username" class="form-control" :value="auth.user.username" readonly />
            <div class="form-text">{{ $gettext('The username cannot be changed.') }}</div>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-12 col-sm-6">
              <label class="form-label" for="profile-first">{{ $gettext('First name') }}</label>
              <input id="profile-first" v-model="profile.first_name" class="form-control" maxlength="50" />
            </div>
            <div class="col-12 col-sm-6">
              <label class="form-label" for="profile-last">{{ $gettext('Last name') }}</label>
              <input id="profile-last" v-model="profile.last_name" class="form-control" maxlength="50" />
            </div>
            <div class="form-text" :class="{ 'text-danger': !hasName }">
              {{ $gettext('At least one of first name and last name is required.') }}
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label" for="profile-email">{{ $gettext('Email address') }}</label>
            <input id="profile-email" v-model="profile.email" type="email" class="form-control" autocomplete="email" required />
          </div>
          <div v-if="emailChanged" class="mb-3" data-test="email-password">
            <label class="form-label" for="profile-password">{{ $gettext('Current password (required to change the email address)') }}</label>
            <input id="profile-password" v-model="profile.current_password" type="password" class="form-control" autocomplete="current-password" required />
          </div>
          <button class="btn btn-primary" type="submit" :disabled="!hasName">{{ $gettext('Save') }}</button>
        </form>
      </div>
    </section>

    <section class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('Interface language') }}</h2>
        <select class="form-select w-auto" :value="gettext.current" :aria-label="$gettext('Interface language')" @change="setLanguage(gettext, $event.target.value)">
          <option v-for="(label, code) in UI_LANGUAGES" :key="code" :value="code">{{ label }}</option>
        </select>
      </div>
    </section>

    <section class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('Change password') }}</h2>
        <div v-if="pwMessage" class="alert alert-success" role="status">{{ pwMessage }}</div>
        <div v-if="pwError" class="alert alert-danger" role="alert">{{ pwError }}</div>
        <form @submit.prevent="changePassword">
          <div class="mb-3">
            <label class="form-label" for="current-password">{{ $gettext('Current password') }}</label>
            <input id="current-password" v-model="pw.current" type="password" class="form-control" autocomplete="current-password" required />
          </div>
          <div class="mb-3">
            <label class="form-label" for="next-password">{{ $gettext('New password') }}</label>
            <input id="next-password" v-model="pw.next" type="password" class="form-control" minlength="8" autocomplete="new-password" required />
          </div>
          <div class="mb-3">
            <label class="form-label" for="repeat-password">{{ $gettext('Repeat password') }}</label>
            <input id="repeat-password" v-model="pw.repeat" type="password" class="form-control" autocomplete="new-password" required />
          </div>
          <button class="btn btn-primary" type="submit" :disabled="pw.next !== pw.repeat">{{ $gettext('Change password') }}</button>
        </form>
      </div>
    </section>

    <section class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('One-time code (OTP)') }}</h2>
        <div v-if="otpMessage" class="alert alert-success" role="status">{{ otpMessage }}</div>
        <p data-test="otp-status">
          {{ auth.user.otp_enabled ? $gettext('OTP is enabled.') : $gettext('OTP is not enabled.') }}
        </p>

        <div v-if="!mode" class="d-flex flex-wrap gap-2">
          <button v-if="!auth.user.otp_enabled" class="btn btn-primary" @click="openOtp('enable')">{{ $gettext('Set up OTP') }}</button>
          <template v-else>
            <button class="btn btn-outline-primary" @click="openOtp('enable')">{{ $gettext('Reset OTP') }}</button>
            <button class="btn btn-outline-danger" @click="openOtp('disable')">{{ $gettext('Disable OTP') }}</button>
          </template>
        </div>

        <template v-else-if="stage === 'form'">
          <div v-if="otpError" class="alert alert-danger" role="alert">{{ otpError }}</div>
          <form @submit.prevent="submitOtpForm">
            <div class="mb-3">
              <label class="form-label" for="otp-password">{{ $gettext('Password') }}</label>
              <input id="otp-password" v-model="otpForm.password" type="password" class="form-control" autocomplete="current-password" required />
            </div>
            <div v-if="auth.user.otp_enabled" class="mb-3">
              <label class="form-label" for="otp-current">{{ $gettext('Current one-time code') }}</label>
              <input id="otp-current" v-model="otpForm.otp" class="form-control" inputmode="numeric" autocomplete="one-time-code" required />
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-primary" type="submit">{{ $gettext('Continue') }}</button>
              <button class="btn btn-outline-secondary" type="button" @click="mode = null">{{ $gettext('Cancel') }}</button>
            </div>
          </form>
        </template>

        <OtpSetup v-else :start="startOtp" :confirm="confirmOtp" @done="otpDone" />
      </div>
    </section>
  </div>
</template>
