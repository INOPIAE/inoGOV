
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'

const props = defineProps({ page: String })
const { $gettext } = useGettext()

const legalHtml = ref('')
const legalError = ref(false)

const legalFiles = {
  terms: '/legal/terms-of-service.de.html',
  privacy: '/legal/data-protection.de.html',
}

const pages = computed(() => ({
  about: {
    title: $gettext('About us'),
    text: $gettext('Information about the project and its operators will be published here.'),
  },
  imprint: {
    title: $gettext('Imprint'),
    text: $gettext('The legal notice will be published here.'),
  },
  privacy: {
    title: $gettext('Privacy'),
    text: '',
  },
  terms: {
    title: $gettext('Terms of Service'),
    text: '',
  },
}))

async function loadLegalPage(page) {
  legalHtml.value = ''
  legalError.value = false

  const file = legalFiles[page]
  if (!file) return

  try {
    const response = await fetch(file)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    legalHtml.value = await response.text()
  } catch (error) {
    console.error(`Error loading ${file}:`, error)
    legalError.value = true
  }
}

onMounted(() => {
  if (legalFiles[props.page]) {
    loadLegalPage(props.page)
  }
})

watch(
  () => props.page,
  (page) => {
    if (legalFiles[page]) {
      loadLegalPage(page)
    } else {
      legalHtml.value = ''
      legalError.value = false
    }
  },
)
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

      <div v-else-if="legalHtml" v-html="legalHtml"></div>

      <p v-else class="text-muted">
        {{ $gettext('Loading...') }}
      </p>
    </template>

    <p v-else>
      {{ pages[props.page]?.text }}
    </p>
  </div>
</template>
