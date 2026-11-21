<script setup>
import { computed, ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import packageInfo from '../../package.json'

const gettext = useGettext()
const version = packageInfo.version
const language = computed(() => gettext.current)
const aboutHtml = ref('')
const loading = ref(false)
const error = ref(false)
let loadRequest = 0

async function loadAbout(languageCode) {
  const request = ++loadRequest
  loading.value = true
  error.value = false
  aboutHtml.value = ''

  try {
    const response = await fetch(`/home/about.${languageCode}.md`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const markdown = await response.text()
    const html = await marked.parse(markdown)

    const cleanHtml = DOMPurify.sanitize(html)

    const doc = new DOMParser().parseFromString(cleanHtml, 'text/html')

    doc.querySelectorAll('a[href]').forEach(link => {
      link.setAttribute('target', '_blank')
      link.setAttribute('rel', 'noopener noreferrer')
    })

    if (request === loadRequest) {
      aboutHtml.value = doc.body.innerHTML
    }

  } catch {
    if (request === loadRequest) error.value = true
  } finally {
    if (request === loadRequest) loading.value = false
  }
}

watch(language, loadAbout, { immediate: true })
</script>

<template>
  <article class="about-page col-12 col-lg-8">
    <header class="mb-4">
      <h1 class="h3 mb-3">{{ gettext.$gettext('About inoGOV') }}</h1>
      <p class="lead mb-0">
        {{ gettext.$gettext('inoGOV helps document historical places and their geographical context, including names, districts, coordinates and map references.') }}
      </p>
    </header>

    <section class="about-section" aria-labelledby="about-project">
      <h2 id="about-project" class="h5">{{ gettext.$gettext('Project information') }}</h2>
      <p v-if="loading" class="text-muted">{{ gettext.$gettext('Loading...') }}</p>
      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ gettext.$gettext('About text could not be loaded.') }}
      </div>
      <article v-else class="about-content" data-test="about-content" v-html="aboutHtml"></article>
    </section>

    <section class="about-section" aria-labelledby="about-version">
      <h2 id="about-version" class="h5">{{ gettext.$gettext('Version') }}</h2>
      <p data-test="version">{{ version }}</p>
    </section>

    <section class="about-section" aria-labelledby="about-license">
      <h2 id="about-license" class="h5">{{ gettext.$gettext('License') }}</h2>
      <p>{{ gettext.$gettext('inoGOV is licensed under the GNU Affero General Public License, version 3 or later.') }}</p>
      <p><code>AGPL-3.0-or-later</code></p>
      <a href="/legal/LICENSE" target="_blank" rel="noopener">
        {{ gettext.$gettext('View full license') }}
      </a>
    </section>

    <section class="about-section" aria-labelledby="about-third-party">
      <h2 id="about-third-party" class="h5">{{ gettext.$gettext('Third-party components') }}</h2>
      <p>{{ gettext.$gettext('Third-party software used by inoGOV and its license information are listed here.') }}</p>
      <a href="/legal/THIRD-PARTY-LICENSES.md" target="_blank" rel="noopener">
        {{ gettext.$gettext('View third-party licenses') }}
      </a>
    </section>

    <section class="about-section" aria-labelledby="about-source">
      <h2 id="about-source" class="h5">{{ gettext.$gettext('Source code') }}</h2>
      <p>{{ gettext.$gettext('The inoGOV source code is available on GitHub.') }}</p>
      <a href="https://github.com/INOPIAE/inogov" target="_blank" rel="noopener">
        {{ gettext.$gettext('View source code') }}
      </a>
    </section>
  </article>
</template>

<style scoped>
.about-section {
  padding: 1rem 0;
  border-top: 1px solid var(--bs-border-color);
}

.about-content {
  line-height: 1.6;
  overflow-wrap: anywhere;
}
</style>