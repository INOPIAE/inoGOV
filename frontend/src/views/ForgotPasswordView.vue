<script setup>
import { ref } from 'vue'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'

const { errorText } = useErrors()
const email = ref('')
const sent = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await api('/auth/forgot-password', { method: 'POST', body: { email: email.value }, auth: false })
    sent.value = true
  } catch (e) {
    error.value = errorText(e)
  }
}
</script>

<template>
  <div class="col-12 col-md-6 col-lg-4 mx-auto">
    <h1 class="h3 mb-3">{{ $gettext('Reset password') }}</h1>
    <div v-if="sent" class="alert alert-success" role="status" data-test="sent">
      {{ $gettext('If the address is known, an email with a link has been sent.') }}
    </div>
    <template v-else>
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label" for="email">{{ $gettext('Email address') }}</label>
          <input id="email" v-model="email" type="email" class="form-control" autocomplete="email" required />
        </div>
        <button class="btn btn-primary w-100" type="submit">{{ $gettext('Send link') }}</button>
      </form>
    </template>
    <p class="mt-3"><router-link to="/login">{{ $gettext('Back to login') }}</router-link></p>
  </div>
</template>
