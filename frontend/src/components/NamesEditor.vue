<script setup>
import { computed, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { useSettingsStore } from '../stores/settings'

// items: [{ id, sprache_id, text }]
const props = defineProps({ items: { type: Array, default: () => [] }, label: String })
const emit = defineEmits(['add', 'remove'])

const gettext = useGettext()
const settings = useSettingsStore()
const spracheId = ref('')
const text = ref('')

const languageLabel = computed(() => (id) => settings.sprachen.find((s) => s.id === id)?.sprache_land ?? '?')

function add() {
  if (!spracheId.value || !text.value.trim()) return
  emit('add', { sprache_id: spracheId.value, text: text.value.trim() })
  text.value = ''
}
</script>

<template>
  <div>
    <h3 class="h6">{{ label }}</h3>
    <ul class="list-group mb-2">
      <li v-for="item in props.items" :key="item.id" class="list-group-item d-flex justify-content-between align-items-center">
        <span>{{ item.text }} <small class="text-muted">({{ languageLabel(item.sprache_id) }})</small></span>
        <button type="button" class="btn btn-sm btn-outline-danger" @click="emit('remove', item.id)">
          {{ gettext.$gettext('Remove') }}
        </button>
      </li>
    </ul>
    <div class="row g-2">
      <div class="col-12 col-sm-4">
        <select v-model="spracheId" class="form-select" :aria-label="gettext.$gettext('Language')">
          <option value="" disabled>{{ gettext.$gettext('Language') }}</option>
          <option v-for="s in settings.sprachen" :key="s.id" :value="s.id">{{ s.sprache_land }}</option>
        </select>
      </div>
      <div class="col-8 col-sm-6">
        <input v-model="text" class="form-control" :aria-label="label" @keyup.enter="add" />
      </div>
      <div class="col-4 col-sm-2">
        <button type="button" class="btn btn-outline-primary w-100" @click="add">{{ gettext.$gettext('Add') }}</button>
      </div>
    </div>
  </div>
</template>
