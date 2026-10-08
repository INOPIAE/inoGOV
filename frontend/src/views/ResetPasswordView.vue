<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'

const route = useRoute()
const { errorText } = useErrors()
const token = String(route.query.token ?? '')
const valid = ref(null)
const info = ref(null)
const password = ref('')
const repeat = ref('')
const done = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    info.value = await api('/auth/link-info', { params: { token }, auth: false })
    valid.value = true
  } catch {
    valid.value = false
  }
})

async function submit() {
  if (password.value !== repeat.value) return
  error.value = ''
  try {
    await api('/auth/reset-password', { method: 'POST', body: { token, new_password: password.value }, auth: false })
    done.value = true
  } catch (e) {
    error.value = errorText(e)
  }
}
</script>

<template>
  <div class="col-12 col-md-6 col-lg-4 mx-auto">
    <h1 class="h3 mb-3">{{ $gettext('Set a new password') }}</h1>
    <div v-if="valid === false" class="alert alert-danger" role="alert" data-test="invalid">
      {{ $gettext('This link is invalid or has expired.') }}
    </div>
    <div v-else-if="done" class="alert alert-success" role="status" data-test="done">
      {{ $gettext('Your password has been changed.') }}
      <router-link to="/login">{{ $gettext('Log in') }}</router-link>
    </div>
    <template v-else-if="valid">
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label" for="new-password">{{ $gettext('New password') }}</label>
          <input id="new-password" v-model="password" type="password" class="form-control" minlength="8" autocomplete="new-password" required />
          <div class="form-text">{{ $gettext('At least 8 characters.') }}</div>
        </div>
        <div class="mb-3">
          <label class="form-label" for="repeat-password">{{ $gettext('Repeat password') }}</label>
          <input id="repeat-password" v-model="repeat" type="password" class="form-control" autocomplete="new-password" required />
          <div v-if="repeat && repeat !== password" class="text-danger small">{{ $gettext('The passwords do not match.') }}</div>
        </div>
        <button class="btn btn-primary w-100" type="submit" :disabled="password !== repeat">{{ $gettext('Save') }}</button>
      </form>
    </template>
  </div>
</template>
