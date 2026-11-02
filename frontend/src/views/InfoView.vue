
<script setup>
import { computed, ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({ page: String })
const gettext = useGettext()
const { $gettext } = gettext
const language = computed(() => gettext.current)

const legalHtml = ref('')
const legalError = ref(false)
const legalLoading = ref(false)
const fallbackUsed = ref(false)

// Dateien liegen im Verzeichnis public/legal/
const legalFiles = {
  imprint: {
    file: (languageCode) => `/legal/imprint.${languageCode}.html`,
    fallback: '/legal/imprint.de.html',
    format: 'html',
  },
  terms: {
    file: (languageCode) => `/legal/terms-of-service.${languageCode}.html`,
    fallback: '/legal/terms-of-service.de.html',
    format: 'html',
  },
  privacy: {
    file: (languageCode) => `/legal/data-protection.${languageCode}.html`,
    fallback: '/legal/data-protection.de.html',
    format: 'html',
  },
  license: {
    file: '/legal/LICENSE',
    format: 'text',
  },
  tp_license: {
    file: '/legal/THIRD-PARTY-LICENSES.md',
    format: 'markdown',
  },
}

const pages = computed(() => ({
  imprint: {
    title: $gettext('Imprint'),
    text: '',
  },
  privacy: {
    title: $gettext('Privacy'),
    text: '',
  },
  terms: {
    title: $gettext('Terms of Service'),
    text: '',
  },
  license: {
    title: $gettext('License'),
    text: '',
  },
  tp_license: {
    title: $gettext('Third-Party Licenses'),
    text: '',
  },
}))

// HTML-Sonderzeichen in Klartext sicher darstellen
function escapeHtml(text) {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

async function loadLegalPage(page) {
  const config = legalFiles[page]

  legalHtml.value = ''
  legalError.value = false
  fallbackUsed.value = false

  if (!config) {
    legalLoading.value = false
    return
  }

  legalLoading.value = true

  try {
    const file = typeof config.file === 'function' ? config.file(language.value) : config.file
    const candidates = [file]
    if (config.fallback && config.fallback !== file) candidates.push(config.fallback)
    let content
    let lastError

    for (const candidate of candidates) {
      try {
        const response = await fetch(candidate)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        content = await response.text()
        if (/<div\s+id=["']app["']\s*>\s*<\/div>/i.test(content)) {
          throw new Error('SPA fallback returned instead of legal content')
        }
        fallbackUsed.value = candidate !== file
        break
      } catch (error) {
        lastError = error
      }
    }

    if (content === undefined) throw lastError ?? new Error('Legal text unavailable')

    if (config.format === 'markdown') {
      // Markdown formatieren und das erzeugte HTML bereinigen
      const html = marked.parse(content)
      legalHtml.value = DOMPurify.sanitize(html)
    } else if (config.format === 'html') {
      // Auch vorhandene HTML-Dokumente bereinigen
      legalHtml.value = DOMPurify.sanitize(content)
    } else {
      // LICENSE als lesbaren, unveränderten Klartext anzeigen
      legalHtml.value =
        `<pre class="legal-plain-text">${escapeHtml(content)}</pre>`
    }
  } catch (error) {
    console.error(`Error loading ${config.file}:`, error)
    legalError.value = true
  } finally {
    legalLoading.value = false
  }
}

watch([() => props.page, language], ([page]) => loadLegalPage(page), { immediate: true })
</script>

<template>
  <div class="col-12 col-lg-8">
    <h1 class="h3 mb-3">
      {{ pages[props.page]?.title }}
    </h1>

    <template v-if="legalFiles[props.page]">
      <div v-if="legalError" class="alert alert-danger">
        {{ $gettext('The legal text could not be loaded.') }}
      </div>

      <p v-else-if="legalLoading" class="text-muted">
        {{ $gettext('Loading...') }}
      </p>

      <div v-else-if="legalHtml">
        <div v-if="fallbackUsed" class="alert alert-info" role="status">
          {{ $gettext('Forwarded to German version') }}
        </div>
        <article class="legal-content" data-test="legal-content" v-html="legalHtml"></article>
      </div>
    </template>

    <p v-else>
      {{ pages[props.page]?.text }}
    </p>
  </div>
</template>

<style scoped>
.legal-content {
  overflow-wrap: anywhere;
  line-height: 1.6;
}

.legal-content :deep(h1) {
  font-size: 1.75rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.legal-content :deep(h2) {
  font-size: 1.4rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.legal-content :deep(h3) {
  font-size: 1.15rem;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.legal-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.legal-content :deep(th),
.legal-content :deep(td) {
  padding: 0.5rem;
  border: 1px solid var(--bs-border-color, #dee2e6);
  text-align: left;
  vertical-align: top;
}

.legal-content :deep(th) {
  background-color: var(--bs-tertiary-bg, #f8f9fa);
}

.legal-content :deep(pre) {
  padding: 1rem;
  overflow-x: auto;
  background-color: var(--bs-tertiary-bg, #f8f9fa);
  border: 1px solid var(--bs-border-color, #dee2e6);
  border-radius: 0.375rem;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.legal-content :deep(code) {
  overflow-wrap: anywhere;
}

.legal-content :deep(img) {
  max-width: 100%;
  height: auto;
}

.legal-content :deep(blockquote) {
  padding-left: 1rem;
  border-left: 3px solid var(--bs-border-color, #dee2e6);
  color: var(--bs-secondary-color, #6c757d);
}
</style>
