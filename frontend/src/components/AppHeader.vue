<script setup>
import { useGettext } from 'vue3-gettext'
import { UI_LANGUAGES, setLanguage } from '../i18n'
import { useSettingsStore } from '../stores/settings'

defineEmits(['toggle-nav'])
const gettext = useGettext()
const settings = useSettingsStore()
</script>

<template>
  <header class="app-header d-flex align-items-center gap-3 px-3 py-2">
    <button
      class="btn btn-outline-light d-md-none"
      type="button"
      :aria-label="$gettext('Toggle navigation')"
      @click="$emit('toggle-nav')"
    >
      &#9776;
    </button>
    <router-link to="/" class="d-flex align-items-center gap-2 text-decoration-none text-reset">
      <img src="/logo.svg" alt="" width="36" height="36" />
      <span class="fs-4 fw-semibold">{{ settings.appName }}</span>
    </router-link>
    <div class="ms-auto">
      <label class="visually-hidden" for="ui-language">{{ $gettext('Language') }}</label>
      <select
        id="ui-language"
        class="form-select form-select-sm"
        :value="gettext.current"
        @change="setLanguage(gettext, $event.target.value)"
      >
        <option v-for="(label, code) in UI_LANGUAGES" :key="code" :value="code">{{ label }}</option>
      </select>
    </div>
  </header>
</template>
