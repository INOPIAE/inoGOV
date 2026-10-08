<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import { useAuthStore } from '../stores/auth'
import { useErrors } from '../composables/useErrors'

const { $gettext } = useGettext()
const { errorText } = useErrors()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const otp = ref('')
const needsOtp = ref(false)
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    await auth.login(username.value, password.value, otp.value)
    const target = route.query.next
    const next = typeof target === 'string' && target.startsWith('/') && !target.startsWith('//') ? target : '/'
    router.push(next)
  } catch (e) {
    if (e.status === 401 && e.detail === 'otp_required') {
      needsOtp.value = true
    } else if (e.status === 401) {
      error.value = needsOtp.value
        ? $gettext('The code or the credentials are wrong.')
        : $gettext('Username or password is wrong.')
    } else if (e.status === 403) {
      error.value = $gettext('This account is blocked.')
    } else {
      error.value = errorText(e)
    }
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="col-12 col-md-6 col-lg-4 mx-auto">
    <h1 class="h3 mb-3">{{ $gettext('Log in') }}</h1>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label class="form-label" for="username">{{ $gettext('Username') }}</label>
        <input id="username" v-model="username" class="form-control" autocomplete="username" required :readonly="needsOtp" />
      </div>
      <div class="mb-3">
        <label class="form-label" for="password">{{ $gettext('Password') }}</label>
        <input id="password" v-model="password" type="password" class="form-control" autocomplete="current-password" required :readonly="needsOtp" />
      </div>
      <div v-if="needsOtp" class="mb-3">
        <label class="form-label" for="otp">{{ $gettext('One-time code') }}</label>
        <input id="otp" v-model="otp" class="form-control" inputmode="numeric" autocomplete="one-time-code" required autofocus />
      </div>
      <button class="btn btn-primary w-100" type="submit" :disabled="busy">{{ $gettext('Log in') }}</button>
    </form>
    <p class="mt-3">
      <router-link to="/forgot-password">{{ $gettext('Forgot your password?') }}</router-link>
    </p>
  </div>
</template>
