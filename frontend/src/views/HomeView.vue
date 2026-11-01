<script setup>
import { computed, ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useSettingsStore } from '../stores/settings'

const gettext = useGettext()
const { $gettext } = gettext
const router = useRouter()
const settings = useSettingsStore()
const query = ref('')
const welcomeHtml = ref('')
const loading = ref(false)
const loadError = ref(false)
const language = computed(() => gettext.current)
let loadRequest = 0

async function loadWelcome(languageCode) {
  const request = ++loadRequest
  loading.value = true
  loadError.value = false
  welcomeHtml.value = ''

  try {
    const response = await fetch(`/home/welcome.${languageCode}.md`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const markdown = await response.text()
    const html = await marked.parse(markdown)
    if (request === loadRequest) welcomeHtml.value = DOMPurify.sanitize(html)
  } catch {
    if (request === loadRequest) loadError.value = true
  } finally {
    if (request === loadRequest) loading.value = false
  }
}

async function searchPlaces() {
  const value = query.value.trim()
  await router.push({ path: '/orte', query: value ? { q: value } : {} })
}

watch(language, loadWelcome, { immediate: true })
</script>

<template>
  <section class="col-12 col-lg-8">
    <h1 class="h3 mb-3">{{ $gettext('Welcome to inoGov') }}</h1>

    <p v-if="loading" class="text-muted">{{ $gettext('Loading...') }}</p>
    <div v-else-if="loadError" class="alert alert-danger" role="alert">
      {{ $gettext('The welcome text could not be loaded.') }}
    </div>
    <article v-else class="welcome-content" data-test="welcome-content" v-html="welcomeHtml"></article>

    <form v-if="settings.publicSearch" class="row g-2 mt-4" @submit.prevent="searchPlaces">
      <div class="col-12 col-sm">
        <label class="visually-hidden" for="home-place-search">{{ $gettext('Place name') }}</label>
        <input
          id="home-place-search"
          v-model="query"
          class="form-control"
          type="search"
          :placeholder="$gettext('Place name')"
        />
      </div>
      <div class="col-12 col-sm-auto">
        <button class="btn btn-primary w-100" type="submit">{{ $gettext('Search') }}</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.welcome-content {
  overflow-wrap: anywhere;
  line-height: 1.6;
}
</style>