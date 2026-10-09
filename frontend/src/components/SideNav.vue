<script setup>
import { apiBase } from '../api'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { useRouter } from 'vue-router'

defineProps({ open: Boolean })
const auth = useAuthStore()
const settings = useSettingsStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <nav class="app-nav" :class="{ open }" :aria-label="$gettext('Main navigation')">
    <ul class="nav flex-column">
      <template v-if="auth.otpSetupRequired">
        <li class="nav-item"><router-link class="nav-link" to="/account">{{ $gettext('My account') }}</router-link></li>
        <li class="nav-item">
          <button type="button" class="nav-link btn btn-link text-start w-100" @click="logout">{{ $gettext('Log out') }}</button>
        </li>
      </template>
      <template v-else>
      <li v-if="settings.publicSearch || auth.isLoggedIn" class="nav-item">
        <router-link class="nav-link" to="/">{{ $gettext('Search places') }}</router-link>
      </li>

      <template v-if="auth.canEdit">
        <li class="nav-heading">{{ $gettext('Management') }}</li>
        <li class="nav-item"><router-link class="nav-link" to="/manage/orte">{{ $gettext('Places') }}</router-link></li>
        <li class="nav-item"><router-link class="nav-link" to="/manage/kreise">{{ $gettext('Districts') }}</router-link></li>
        <li class="nav-item"><router-link class="nav-link" to="/manage/karten">{{ $gettext('Maps') }}</router-link></li>
      </template>

      <template v-if="auth.isLoggedIn">
        <li class="nav-heading">{{ $gettext('Users') }}</li>
        <li class="nav-item"><router-link class="nav-link" to="/account">{{ $gettext('My account') }}</router-link></li>
        <li v-if="auth.isAdmin" class="nav-item">
          <router-link class="nav-link" to="/users">{{ $gettext('User management') }}</router-link>
        </li>
      </template>

      <li class="nav-heading">{{ $gettext('Information') }}</li>
      <li class="nav-item">
        <a class="nav-link" :href="`${apiBase}/docs`" target="_blank" rel="noopener">{{ $gettext('API documentation') }}</a>
      </li>
      <li class="nav-item"><router-link class="nav-link" to="/about">{{ $gettext('About us') }}</router-link></li>
      <li class="nav-item"><router-link class="nav-link" to="/imprint">{{ $gettext('Imprint') }}</router-link></li>
      <li class="nav-item"><router-link class="nav-link" to="/privacy">{{ $gettext('Privacy') }}</router-link></li>

      <li class="nav-heading">&nbsp;</li>
      <li v-if="auth.isLoggedIn" class="nav-item">
        <button type="button" class="nav-link btn btn-link text-start w-100" @click="logout">{{ $gettext('Log out') }}</button>
      </li>
      <li v-else class="nav-item">
        <router-link class="nav-link" to="/login">{{ $gettext('Log in') }}</router-link>
      </li>
      </template>
    </ul>
  </nav>
</template>
