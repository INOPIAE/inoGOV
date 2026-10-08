<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import OtpSetup from '../components/OtpSetup.vue'

const route = useRoute()
const token = String(route.query.token ?? '')
const valid = ref(null)
const done = ref(false)

onMounted(async () => {
  try {
    const info = await api('/auth/link-info', { params: { token }, auth: false })
    valid.value = info.purpose === 'otp_reset'
  } catch {
    valid.value = false
  }
})

const start = () => api('/auth/otp/start', { method: 'POST', body: { token }, auth: false })
const confirm = (setupToken, code) =>
  api('/auth/otp/confirm', { method: 'POST', body: { token, setup_token: setupToken, code }, auth: false })
</script>

<template>
  <div class="col-12 col-md-8 col-lg-5 mx-auto">
    <h1 class="h3 mb-3">{{ $gettext('Set up OTP') }}</h1>
    <div v-if="valid === false" class="alert alert-danger" role="alert" data-test="invalid">
      {{ $gettext('This link is invalid or has expired.') }}
    </div>
    <div v-else-if="done" class="alert alert-success" role="status" data-test="done">
      {{ $gettext('OTP has been set up.') }}
      <router-link to="/login">{{ $gettext('Log in') }}</router-link>
    </div>
    <OtpSetup v-else-if="valid" :start="start" :confirm="confirm" @done="done = true" />
  </div>
</template>
