<script setup>
import { computed, onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'
import { useSettingsStore } from '../stores/settings'

const gettext = useGettext()
const { $gettext } = gettext
const { errorText } = useErrors()
const settings = useSettingsStore()

const q = ref('')
const list = ref([])
const ort = ref(null)
const newKarte = ref({ karte: '', koordinate: '' })
const error = ref('')

const language = computed(() => gettext.current)
const label = (o) => settings.pickName(o.namen, 'ortsname', language.value) || o.gov_id || '?'

async function guard(action) {
  error.value = ''
  try {
    await action()
  } catch (e) {
    error.value = errorText(e)
  }
}

const loadList = () => guard(async () => (list.value = await api('/orte', { params: { q: q.value.trim(), limit: 50 } })))
const refresh = async () => (ort.value = await api(`/orte/${ort.value.id}`))

const add = () =>
  guard(async () => {
    await api(`/orte/${ort.value.id}/karten`, {
      method: 'POST',
      body: { karte: newKarte.value.karte.trim() || null, koordinate: newKarte.value.koordinate.trim() || null },
    })
    newKarte.value = { karte: '', koordinate: '' }
    await refresh()
  })

const remove = (karteId) =>
  guard(async () => {
    await api(`/orte/${ort.value.id}/karten/${karteId}`, { method: 'DELETE' })
    await refresh()
  })

onMounted(async () => {
  await guard(() => settings.loadReference())
  await loadList()
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Maps') }}</h1>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <div class="row g-4">
      <div class="col-12 col-lg-5">
        <form class="input-group mb-2" @submit.prevent="loadList">
          <input v-model="q" type="search" class="form-control" :placeholder="$gettext('Place name')" :aria-label="$gettext('Place name')" />
          <button class="btn btn-outline-primary" type="submit">{{ $gettext('Search') }}</button>
        </form>
        <div class="list-group">
          <button
            v-for="o in list"
            :key="o.id"
            type="button"
            class="list-group-item list-group-item-action"
            :class="{ active: ort?.id === o.id }"
            data-test="list-item"
            @click="ort = o"
          >
            {{ label(o) }}
          </button>
        </div>
      </div>

      <div v-if="ort" class="col-12 col-lg-7">
        <div class="card card-body">
          <h2 class="h5">{{ label(ort) }}</h2>
          <ul class="list-group mb-3">
            <li v-for="k in ort.karten" :key="k.id" class="list-group-item d-flex justify-content-between align-items-center">
              <span>{{ k.karte }} {{ k.koordinate }}</span>
              <button class="btn btn-sm btn-outline-danger" @click="remove(k.id)">{{ $gettext('Remove') }}</button>
            </li>
            <li v-if="!ort.karten.length" class="list-group-item text-muted">{{ $gettext('No map references yet.') }}</li>
          </ul>
          <form class="row g-2" @submit.prevent="add">
            <div class="col-6 col-sm-5">
              <input v-model="newKarte.karte" class="form-control" maxlength="10" :placeholder="$gettext('Map')" :aria-label="$gettext('Map')" required />
            </div>
            <div class="col-6 col-sm-4">
              <input v-model="newKarte.koordinate" class="form-control" maxlength="2" :placeholder="$gettext('Grid square')" :aria-label="$gettext('Grid square')" />
            </div>
            <div class="col-12 col-sm-3">
              <button class="btn btn-primary w-100" type="submit">{{ $gettext('Add') }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
