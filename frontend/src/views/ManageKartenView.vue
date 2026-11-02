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
const onlineMaps = ref([])
const regionalMaps = ref([])
const regionalMapId = ref('')
const onlineMapForm = ref(null)
const message = ref('')
const error = ref('')

const language = computed(() => gettext.current)
const availableOnlineMaps = computed(() =>
  onlineMaps.value.filter(
    (onlineMap) =>
      !onlineMap.global &&
      !regionalMaps.value.some((assignment) => assignment.map_online_id === onlineMap.id),
  ),
)
const label = (o) => settings.pickName(o.namen, 'ortsname', language.value) || o.gov_id || '?'

async function guard(action) {
  error.value = ''
  message.value = ''
  try {
    await action()
  } catch (e) {
    error.value = errorText(e)
  }
}

const loadList = () => guard(async () => (list.value = await api('/orte', { params: { q: q.value.trim(), limit: 50 } })))
const refresh = async () => (ort.value = await api(`/orte/${ort.value.id}`))
const loadRegionalMaps = (ortId) =>
  guard(async () => {
    const assignments = await api('/regional-maps', { params: { ort_id: ortId } })
    regionalMaps.value = assignments.filter((assignment) => !assignment.map_online.global)
    regionalMapId.value = ''
  })
const loadOnlineMaps = () => guard(async () => (onlineMaps.value = await api('/map-online')))
const selectOrt = (selected) => {
  ort.value = selected
  loadRegionalMaps(selected.id)
}

const newOnlineMap = () => {
  onlineMapForm.value = {
    id: null,
    mapname: '',
    map_short: '',
    map_url_basis: '',
    map_url_pattern: '',
    global: false,
  }
}

const editOnlineMap = (onlineMap) => {
  onlineMapForm.value = { ...onlineMap }
}

const saveOnlineMap = () =>
  guard(async () => {
    const form = onlineMapForm.value
    const body = {
      mapname: form.mapname.trim(),
      map_short: form.map_short.trim(),
      map_url_basis: form.map_url_basis.trim(),
      map_url_pattern: form.map_url_pattern.trim(),
      global: form.global,
    }
    const saved = form.id
      ? await api(`/map-online/${form.id}`, { method: 'PATCH', body })
      : await api('/map-online', { method: 'POST', body })
    await loadOnlineMaps()
    onlineMapForm.value = saved
    if (ort.value) await loadRegionalMaps(ort.value.id)
    message.value = $gettext('Saved.')
  })

const deleteOnlineMap = () =>
  guard(async () => {
    if (!onlineMapForm.value?.id || !window.confirm($gettext('Really delete this online map?'))) return
    await api(`/map-online/${onlineMapForm.value.id}`, { method: 'DELETE' })
    onlineMapForm.value = null
    await loadOnlineMaps()
    if (ort.value) await loadRegionalMaps(ort.value.id)
  })

const assignOnlineMap = () =>
  guard(async () => {
    if (!ort.value || !regionalMapId.value) return
    await api('/regional-maps', {
      method: 'POST',
      body: { ort_id: ort.value.id, map_online_id: regionalMapId.value },
    })
    await loadRegionalMaps(ort.value.id)
  })

const removeOnlineMap = (regionalMap) =>
  guard(async () => {
    await api(`/regional-maps/${regionalMap.id}`, { method: 'DELETE' })
    await loadRegionalMaps(ort.value.id)
  })

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
  await loadOnlineMaps()
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Maps') }}</h1>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="message" class="alert alert-success" role="status">{{ message }}</div>

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
            @click="selectOrt(o)"
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
          <h3 class="h6" data-test="regional-maps-heading">{{ $gettext('Assigned non-global online maps') }}</h3>
          <ul class="list-group mb-3">
            <li v-for="assignment in regionalMaps" :key="assignment.id" class="list-group-item d-flex justify-content-between align-items-center" data-test="regional-online-assignment">
              <span>{{ assignment.map_online.map_short }} · {{ assignment.map_online.mapname }}</span>
              <button type="button" class="btn btn-sm btn-outline-danger" data-test="remove-online-assignment" @click="removeOnlineMap(assignment)">
                {{ $gettext('Remove') }}
              </button>
            </li>
            <li v-if="!regionalMaps.length" class="list-group-item text-muted">{{ $gettext('No online map assignments yet.') }}</li>
          </ul>
          <form class="row g-2 mb-3" data-test="regional-map-form" @submit.prevent="assignOnlineMap">
            <div class="col-8">
              <label class="visually-hidden" for="regional-map-provider">{{ $gettext('Online map') }}</label>
              <select id="regional-map-provider" v-model="regionalMapId" class="form-select" required>
                <option value="" disabled>{{ $gettext('Select online map') }}</option>
                <option v-for="onlineMap in availableOnlineMaps" :key="onlineMap.id" :value="onlineMap.id">
                  {{ onlineMap.map_short }} · {{ onlineMap.mapname }}
                </option>
              </select>
            </div>
            <div class="col-4">
              <button class="btn btn-outline-primary w-100" type="submit" :disabled="!regionalMapId">
                {{ $gettext('Assign') }}
              </button>
            </div>
          </form>
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

    <section class="mt-4" aria-labelledby="online-map-heading">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 id="online-map-heading" class="h5 mb-0">{{ $gettext('Online map providers') }}</h2>
        <button type="button" class="btn btn-primary" data-test="new-online-map" @click="newOnlineMap">{{ $gettext('New online map') }}</button>
      </div>
      <div class="row g-4">
        <div class="col-12 col-lg-5">
          <div class="list-group">
            <button
              v-for="onlineMap in onlineMaps"
              :key="onlineMap.id"
              type="button"
              class="list-group-item list-group-item-action"
              :class="{ active: onlineMapForm?.id === onlineMap.id }"
              data-test="online-map-item"
              @click="editOnlineMap(onlineMap)"
            >
              <strong>{{ onlineMap.map_short }}</strong> · {{ onlineMap.mapname }}
              <span v-if="onlineMap.global" class="text-muted"> · {{ $gettext('Global') }}</span>
            </button>
          </div>
        </div>
        <div v-if="onlineMapForm" class="col-12 col-lg-7">
          <form class="border rounded p-3" data-test="online-map-form" @submit.prevent="saveOnlineMap">
            <h3 class="h6">{{ onlineMapForm.id ? $gettext('Edit online map') : $gettext('New online map') }}</h3>
            <div class="mb-2">
              <label class="form-label" for="mapname">{{ $gettext('Map name') }}</label>
              <input id="mapname" v-model="onlineMapForm.mapname" class="form-control" maxlength="50" required />
            </div>
            <div class="mb-2">
              <label class="form-label" for="map-short">{{ $gettext('Short name') }}</label>
              <input id="map-short" v-model="onlineMapForm.map_short" class="form-control" maxlength="10" required />
            </div>
            <div class="mb-2">
              <label class="form-label" for="map-url-basis">{{ $gettext('Base URL') }}</label>
              <input id="map-url-basis" v-model="onlineMapForm.map_url_basis" class="form-control" maxlength="255" required />
            </div>
            <div class="mb-2">
              <label class="form-label" for="map-url-pattern">{{ $gettext('URL pattern') }}</label>
              <input id="map-url-pattern" v-model="onlineMapForm.map_url_pattern" class="form-control" maxlength="255" required />
            </div>
            <div class="form-check mb-3">
              <input id="map-global" v-model="onlineMapForm.global" type="checkbox" class="form-check-input" />
              <label class="form-check-label" for="map-global">{{ $gettext('Global map') }}</label>
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-primary" type="submit">{{ $gettext('Save') }}</button>
              <button v-if="onlineMapForm.id" class="btn btn-outline-danger" type="button" @click="deleteOnlineMap">
                {{ $gettext('Delete') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>
