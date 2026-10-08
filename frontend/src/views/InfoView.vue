<script setup>
import { computed } from 'vue'
import { useGettext } from 'vue3-gettext'

const props = defineProps({ page: String })
const { $gettext } = useGettext()

// Platzhaltertexte, bis die endgültigen Inhalte vorliegen.
const pages = computed(() => ({
  about: { title: $gettext('About us'), text: $gettext('Information about the project and its operators will be published here.') },
  imprint: { title: $gettext('Imprint'), text: $gettext('The legal notice will be published here.') },
  privacy: { title: $gettext('Privacy'), text: $gettext('The privacy policy will be published here.') },
}))
</script>

<template>
  <div class="col-12 col-lg-8">
    <h1 class="h3 mb-3">{{ pages[props.page].title }}</h1>
    <p>{{ pages[props.page].text }}</p>
  </div>
</template>
