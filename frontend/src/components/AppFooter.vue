<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'

const START_YEAR = 2026
const auth = useAuthStore()
const settings = useSettingsStore()
const years = computed(() => {
  const now = new Date().getFullYear()
  return now > START_YEAR ? `${START_YEAR}\u2013${now}` : `${START_YEAR}`
})
</script>

<template>
  <footer class="app-footer d-flex flex-wrap justify-content-between gap-2 px-3 py-2">
    <span v-if="auth.isLoggedIn" data-test="login-state">
      {{ $gettext('Signed in as %{user} (%{roles})', { user: auth.user.username, roles: auth.roles.join(', ') || '-' }) }}
    </span>
    <span v-else data-test="login-state">{{ $gettext('Not signed in') }}</span>
    <span data-test="copyright">&copy; {{ years }} {{ settings.copyrightName }}</span>
  </footer>
</template>
