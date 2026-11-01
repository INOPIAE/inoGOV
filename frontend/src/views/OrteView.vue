<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'
import { useSettingsStore } from '../stores/settings'
import { useAuthStore } from '../stores/auth'

const LIMIT = 20
const gettext = useGettext()
const { $gettext } = gettext
const { errorText } = useErrors()
const settings = useSettingsStore()
const auth = useAuthStore()
const route = useRoute()

const q = ref(typeof route.query.q === 'string' ? route.query.q : '')
const kreisId = ref('')
const offset = ref(0)
const results = ref([])
const foundCount = ref(0)
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const error = ref('')
const sortColumn = ref('name')
const sortDirection = ref('asc')

const language = computed(() => gettext.current)

function toggleSort(column) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  search(0)
}

function sortState(column) {
  return sortColumn.value === column ? (sortDirection.value === 'asc' ? 'ascending' : 'descending') : 'none'
}

async function search(newOffset = 0) {
  offset.value = newOffset
  loading.value = true
  error.value = ''
  try {
    const params = { q: q.value.trim(), kreis_id: kreisId.value }
    const [nextResults, counts] = await Promise.all([
      api('/orte', {
        params: {
          ...params,
          limit: LIMIT,
          offset: newOffset,
          sort_by: sortColumn.value,
          sort_order: sortDirection.value,
          sort_sprache_id: settings.sprachen.find((sprache) => sprache.sprache2 === language.value)?.id,
        },
      }),
      api('/orte/count', { params }),
    ])
    results.value = nextResults
    foundCount.value = counts.found
    totalCount.value = counts.total
    searched.value = true
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}

const govUrl = (ort) => `https://gov.genealogy.net/item/show/${encodeURIComponent(ort.gov_id)}`
const mapUrl = (ort) => `https://etomesto.com/map-ukraine_spezialkarte-uk-750/?y=${ort.lat}&x=${ort.lon}`
const osmURL = (ort) => `https://www.openstreetmap.org/?mlat=${ort.lat}&mlon=${ort.lon}#map=9/${ort.lat}/${ort.lon}` 
const otherNames = (ort) => ort.namen.filter((n) => n.ortsname !== settings.pickName(ort.namen, 'ortsname', language.value))

onMounted(async () => {
  try {
    await settings.loadReference()
  } catch (e) {
    error.value = errorText(e)
  }
  await search()
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Search places') }}</h1>

    <form class="row g-2 mb-3" @submit.prevent="search(0)">
      <div class="col-12 col-md-6">
        <label class="visually-hidden" for="q">{{ $gettext('Place name') }}</label>
        <input id="q" v-model="q" class="form-control" type="search" :placeholder="$gettext('Place name')" />
      </div>
      <div class="col-8 col-md-4">
        <label class="visually-hidden" for="kreis">{{ $gettext('District') }}</label>
        <select id="kreis" v-model="kreisId" class="form-select" @change="search(0)">
          <option value="">{{ $gettext('All districts') }}</option>
          <option v-for="k in settings.kreise" :key="k.id" :value="k.id">
            {{ settings.pickName(k.namen, 'kreisname', language) || k.gov_id }}
          </option>
        </select>
      </div>
      <div class="col-4 col-md-2">
        <button class="btn btn-primary w-100" type="submit" :disabled="loading">{{ $gettext('Search') }}</button>
      </div>
    </form>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <p v-if="searched && !results.length && !error" data-test="empty">{{ $gettext('No places found.') }}</p>

    <div v-if="searched && (offset > 0 || results.length === LIMIT)" class="d-flex gap-2">
      <button class="btn btn-outline-primary" :disabled="offset === 0 || loading" @click="search(offset - LIMIT)">
        {{ $gettext('Previous') }}
      </button>
      <button class="btn btn-outline-primary" :disabled="results.length < LIMIT || loading" @click="search(offset + LIMIT)">
        {{ $gettext('Next') }}
      </button>
    </div>

    <div v-if="results.length" class="table-responsive">
      <table class="table table-hover align-middle">
        <thead>
          <tr>
            <th :aria-sort="sortState('name')">
              <button class="btn btn-link p-0 fw-semibold text-body text-decoration-none" data-sort="name" type="button" :disabled="loading" @click="toggleSort('name')">
                {{ $gettext('Place') }} <span aria-hidden="true">{{ sortColumn === 'name' ? (sortDirection === 'asc' ? '▲' : '▼') : '' }}</span>
              </button>
            </th>
            <th :aria-sort="sortState('district')">
              <button class="btn btn-link p-0 fw-semibold text-body text-decoration-none" data-sort="district" type="button" :disabled="loading" @click="toggleSort('district')">
                {{ $gettext('District') }} <span aria-hidden="true">{{ sortColumn === 'district' ? (sortDirection === 'asc' ? '▲' : '▼') : '' }}</span>
              </button>
            </th>
            <th :aria-sort="sortState('coordinates')">
              <button class="btn btn-link p-0 fw-semibold text-body text-decoration-none" data-sort="coordinates" type="button" :disabled="loading" @click="toggleSort('coordinates')">
                {{ $gettext('Coordinates') }} <span aria-hidden="true">{{ sortColumn === 'coordinates' ? (sortDirection === 'asc' ? '▲' : '▼') : '' }}</span>
              </button>
            </th>
            <th :aria-sort="sortState('maps')">
              <button class="btn btn-link p-0 fw-semibold text-body text-decoration-none" data-sort="maps" type="button" :disabled="loading" @click="toggleSort('maps')">
                {{ $gettext('Maps') }} <span aria-hidden="true">{{ sortColumn === 'maps' ? (sortDirection === 'asc' ? '▲' : '▼') : '' }}</span>
              </button>
            </th>
            <th :aria-sort="sortState('links')">
              <button class="btn btn-link p-0 fw-semibold text-body text-decoration-none" data-sort="links" type="button" :disabled="loading" @click="toggleSort('links')">
                {{ $gettext('Links') }} <span aria-hidden="true">{{ sortColumn === 'links' ? (sortDirection === 'asc' ? '▲' : '▼') : '' }}</span>
              </button>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ort in results" :key="ort.id" data-test="result">
            <td>
              <strong>{{ settings.pickName(ort.namen, 'ortsname', language) || ort.gov_id }}</strong>
              <div v-if="otherNames(ort).length" class="small text-muted">
                {{ otherNames(ort).map((n) => n.ortsname).join(', ') }}
              </div>
            </td>
            <td>{{ settings.kreisName(ort.kreis_id, language) }}</td>
            <td>
              <span v-if="ort.lat && ort.lon">{{ ort.lat }}, {{ ort.lon }}</span>
              <span v-if="ort.coordinates_not_found">{{ $gettext('Coordinates not found') }}</span>
            </td>
            <td>
              <div v-for="k in ort.karten" :key="k.id">
                <router-link
                  v-if="auth.isLoggedIn && k.karte && k.koordinate"
                  :to="{ name: 'map', params: { karte: k.karte, koordinate: k.koordinate } }"
                  target="_blank"
                  rel="noopener"
                  data-test="map-link"
                >
                  {{ k.karte }} {{ k.koordinate }}
                </router-link>

                <span v-else>{{ k.karte }} {{ k.koordinate }}</span>
              </div>
            </td>
            <td class="text-nowrap">
              <a v-if="ort.gov_id" :href="govUrl(ort)" target="_blank" rel="noopener">GOV</a>
              <a v-if="ort.lat && ort.lon" class="ms-2" :href="mapUrl(ort)" target="_blank" rel="noopener">{{ $gettext('Map') }}</a>
              <a v-if="ort.lat && ort.lon" class="ms-2" :href="osmURL(ort)" target="_blank" rel="noopener">{{ $gettext('OSM') }}</a>  
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="searched && (offset > 0 || results.length === LIMIT)" class="d-flex gap-2">
      <button class="btn btn-outline-primary" :disabled="offset === 0 || loading" @click="search(offset - LIMIT)">
        {{ $gettext('Previous') }}
      </button>
      <button class="btn btn-outline-primary" :disabled="results.length < LIMIT || loading" @click="search(offset + LIMIT)">
        {{ $gettext('Next') }}
      </button>
    </div>

    <p v-if="searched" class="small text-muted mt-2" data-test="result-count">
      {{ $gettext('Found %{found} of %{total} places.', { found: foundCount, total: totalCount }) }}
    </p>

  </div>
</template>
