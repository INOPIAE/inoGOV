<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'

const props = defineProps({ page: String })
const { $gettext } = useGettext()

const termsHtml = ref('')
const termsError = ref(false)

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
    text: $gettext('The privacy policy will be published here.'),
  },
  terms: {
    title: $gettext('Terms of Service'),
    text: '',
  },
}))

async function loadTerms() {
  termsHtml.value = ''
  termsError.value = false

  try {
    const response = await fetch('/legal/terms-of-service.de.html')

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    termsHtml.value = await response.text()
  } catch (error) {
    console.error('Error loading terms.html:', error)
    termsError.value = true
  }
}

onMounted(() => {
  if (props.page === 'terms') {
    loadTerms()
  }
})

watch(() => props.page, (page) => {
  if (page === 'terms') {
    loadTerms()
  }
})
</script>

<template>
  <div class="col-12 col-lg-8">
    <h1 class="h3 mb-3">{{ pages[props.page]?.title }}</h1>

    <template v-if="props.page === 'terms'">
      <div v-if="termsError" class="alert alert-danger">
        {{ $gettext('The terms of service could not be loaded.') }}
      </div>

      <div v-else-if="termsHtml" v-html="termsHtml"></div>

      <p v-else class="text-muted">
        {{ $gettext('Loading...') }}
      </p>
    </template>

    <p v-else>{{ pages[props.page]?.text }}</p>
  </div>
</template>
