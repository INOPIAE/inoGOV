<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'
import { useErrors } from '../composables/useErrors'
import OtpSetup from '../components/OtpSetup.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { errorText } = useErrors()
const token = String(route.query.token ?? '')

const valid = ref(null)
const info = ref(null)
const username = ref('')
const password = ref('')
const repeat = ref('')
const error = ref('')
// 'account' -> 'otp' (optional) -> fertig
const step = ref('account')

onMounted(async () => {
  try {
    info.value = await api('/auth/link-info', { params: { token }, auth: false })
    valid.value = info.value.purpose === 'invite'
  } catch {
    valid.value = false
  }
})

async function submit() {
  error.value = ''
  try {
    const data = await api('/auth/setup-account', {
      method: 'POST',
      body: { token, username: username.value, password: password.value },
      auth: false,
    })
    await auth.acceptToken(data.access_token)
    step.value = 'otp-choice'
  } catch (e) {
    error.value = errorText(e)
  }
}

const startOtp = () => api('/users/me/otp/start', { method: 'POST', body: { password: password.value } })
const confirmOtp = (setupToken, code) =>
  api('/users/me/otp/confirm', { method: 'POST', body: { setup_token: setupToken, code } })
const finish = () => router.push('/')
</script>

<template>
  <div class="col-12 col-md-8 col-lg-5 mx-auto">
    <h1 class="h3 mb-3">{{ $gettext('Set up your account') }}</h1>

    <div v-if="valid === false" class="alert alert-danger" role="alert" data-test="invalid">
      {{ $gettext('This link is invalid or has expired.') }}
    </div>

    <template v-else-if="valid && step === 'account'">
      <p>{{ $gettext('Welcome! Choose a username and a password for %{email}.', { email: info.email }) }}</p>
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label" for="username">{{ $gettext('Username') }}</label>
          <input id="username" v-model="username" class="form-control" maxlength="50" autocomplete="username" required />
        </div>
        <div class="mb-3">
          <label class="form-label" for="password">{{ $gettext('Password') }}</label>
          <input id="password" v-model="password" type="password" class="form-control" minlength="8" autocomplete="new-password" required />
          <div class="form-text">{{ $gettext('At least 8 characters.') }}</div>
        </div>
        <div class="mb-3">
          <label class="form-label" for="repeat">{{ $gettext('Repeat password') }}</label>
          <input id="repeat" v-model="repeat" type="password" class="form-control" autocomplete="new-password" required />
          <div v-if="repeat && repeat !== password" class="text-danger small">{{ $gettext('The passwords do not match.') }}</div>
        </div>
        <button class="btn btn-primary w-100" type="submit" :disabled="password !== repeat">{{ $gettext('Continue') }}</button>
      </form>
    </template>

    <template v-else-if="step === 'otp-choice'">
      <p>{{ $gettext('Your account is ready. You can protect it with a one-time code (OTP) now or later in "My account".') }}</p>
      <div class="d-flex gap-2">
        <button class="btn btn-primary" @click="step = 'otp'">{{ $gettext('Set up OTP') }}</button>
        <button class="btn btn-outline-secondary" @click="finish">{{ $gettext('Skip') }}</button>
      </div>
    </template>

    <OtpSetup v-else-if="step === 'otp'" :start="startOtp" :confirm="confirmOtp" @done="finish" />
  </div>
</template>
