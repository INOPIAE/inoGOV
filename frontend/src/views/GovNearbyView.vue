<script setup>
import { ref, watch } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'
import { boundingRange, distanceOptions } from '../composables/govBox'

const gettext = useGettext()
const { errorText } = useErrors()

const latitude = ref('')
const longitude = ref('')
const latDistance = ref(0.05)
const lonDistance = ref(0.05)
const latitude0 = ref('')
const latitude1 = ref('')
const longitude0 = ref('')
const longitude1 = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const error = ref('')

watch([latitude, latDistance], () => {
  if (latitude.value === '' || Number.isNaN(Number(latitude.value))) return
  ;[latitude0.value, latitude1.value] = boundingRange(latitude.value, latDistance.value)
})

watch([longitude, lonDistance], () => {
  if (longitude.value === '' || Number.isNaN(Number(longitude.value))) return
  ;[longitude0.value, longitude1.value] = boundingRange(longitude.value, lonDistance.value)
})

const hasArea = () =>
  [latitude0, latitude1, longitude0, longitude1].every((v) => v.value !== '' && !Number.isNaN(Number(v.value)))

async function search() {
  if (loading.value || !hasArea()) return
  loading.value = true
  error.value = ''
  results.value = []
  try {
    results.value = await api('/gov_suche_nearby', {
      params: {
        latitude0: latitude0.value,
        latitude1: latitude1.value,
        longitude0: longitude0.value,
        longitude1: longitude1.value,
      },
    })
    searched.value = true
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ gettext.$gettext('GOV nearby search') }}</h1>

    <form class="row g-3 mb-3 nearby-search" @submit.prevent="search">
      <div class="col-md-3">
        <label class="form-label" for="nearby-latitude">{{ gettext.$gettext('Latitude') }}</label>
        <input id="nearby-latitude" v-model="latitude" class="form-control" inputmode="decimal" />
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-lat-distance">{{ gettext.$gettext('Latitude distance') }}</label>
        <select id="nearby-lat-distance" v-model.number="latDistance" class="form-select">
          <option v-for="d in distanceOptions" :key="d" :value="d">{{ d.toFixed(2) }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-longitude">{{ gettext.$gettext('Longitude') }}</label>
        <input id="nearby-longitude" v-model="longitude" class="form-control" inputmode="decimal" />
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-lon-distance">{{ gettext.$gettext('Longitude distance') }}</label>
        <select id="nearby-lon-distance" v-model.number="lonDistance" class="form-select">
          <option v-for="d in distanceOptions" :key="d" :value="d">{{ d.toFixed(2) }}</option>
        </select>
      </div>

      <div class="col-md-3">
        <label class="form-label" for="nearby-latitude0">latitude0</label>
        <input id="nearby-latitude0" v-model="latitude0" class="form-control" inputmode="decimal" />
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-latitude1">latitude1</label>
        <input id="nearby-latitude1" v-model="latitude1" class="form-control" inputmode="decimal" />
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-longitude0">longitude0</label>
        <input id="nearby-longitude0" v-model="longitude0" class="form-control" inputmode="decimal" />
      </div>
      <div class="col-md-3">
        <label class="form-label" for="nearby-longitude1">longitude1</label>
        <input id="nearby-longitude1" v-model="longitude1" class="form-control" inputmode="decimal" />
      </div>

      <div class="col-12">
        <button type="submit" class="btn btn-primary" :disabled="loading || !hasArea()">
          {{ loading ? gettext.$gettext('Searching...') : gettext.$gettext('Search') }}
        </button>
      </div>
    </form>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <p v-if="searched && !loading && results.length === 0 && !error" class="text-muted">
      {{ gettext.$gettext('No results found.') }}
    </p>

    <div class="nearby-results">
    <div v-for="result in results" :key="result.id" class="card mb-3" data-test="nearby-result">
      <div class="card-body">
        <div class="d-flex justify-content-between flex-wrap gap-2 mb-2">
          <strong>{{ result.id }}</strong>
          <small v-if="result.position" class="text-muted">
            {{ result.position.lat }}, {{ result.position.lon }}
          </small>
        </div>
        <ul class="list-group">
          <li v-for="(name, index) in result.name" :key="`${result.id}-${index}`" class="list-group-item">
            {{ name.value }} <small class="text-muted">({{ name.lang || '?' }})</small>
          </li>
        </ul>
        <p v-if="!result.name?.length" class="text-muted small mb-0">{{ gettext.$gettext('No names available.') }}</p>
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
.nearby-search {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--bs-body-bg, #fff);
  padding-bottom: 0.5rem;
}

.nearby-results {
  max-height: 60vh;
  overflow-y: auto;
}
</style>
