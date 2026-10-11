
<script setup>
import { computed, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useSettingsStore } from '../stores/settings'

const emit = defineEmits(['add', 'select-place'])

const gettext = useGettext()
const settings = useSettingsStore()

const placename = ref('')
const results = ref([])
const loading = ref(false)
const error = ref('')

// GOV-Sprachcodes auf mögliche Bezeichnungen im Settings-Store abbilden.
const languageAliases = {
  deu: ['deutsch', 'german'],
  eng: ['englisch', 'english'],
  pol: ['polnisch', 'polish', 'polski'],
  rus: ['russisch', 'russian', 'русский'],
  ukr: ['ukrainisch', 'ukrainian', 'українська'],
  ces: ['tschechisch', 'czech', 'čeština'],
  fra: ['französisch', 'french', 'français'],
  nld: ['niederländisch', 'dutch', 'nederlands'],
  ita: ['italienisch', 'italian', 'italiano'],
  spa: ['spanisch', 'spanish', 'español'],
  lat: ['latein', 'latin', 'latina'],
  bel: ['belarussisch', 'belarusian', 'беларуская'],
  dan: ['dänisch', 'danish', 'dansk'],
  swe: ['schwedisch', 'swedish', 'svenska'],
  nor: ['norwegisch', 'norwegian', 'norsk'],
  hun: ['ungarisch', 'hungarian', 'magyar'],
  ron: ['rumänisch', 'romanian', 'română'],
}

function normalize(value) {
  return String(value ?? '')
    .trim()
    .toLocaleLowerCase()
}

function findLanguageId(lang) {
  if (!lang) return null

  const code = normalize(lang)
  const aliases = languageAliases[code] ?? []

  const language = settings.sprachen.find((s) => {
    // Optional vorhandene ISO-Sprachcodefelder berücksichtigen.
    const codes = [
      s.iso639_1,
      s.iso639_2,
      s.iso_639_1,
      s.iso_639_2,
      s.sprache_code,
      s.kuerzel,
      s.code,
    ].filter(Boolean).map(normalize)

    if (codes.includes(code)) return true

    const label = normalize(s.sprache_land)
    return aliases.includes(label)
  })

  return language?.id ?? null
}

const languageLabel = (lang) => {
  const id = findLanguageId(lang)
  return settings.sprachen.find((s) => s.id === id)?.sprache_land ?? lang ?? '?'
}

async function search() {
  const query = placename.value.trim()
  if (!query || loading.value) return

  loading.value = true
  error.value = ''
  results.value = []

  try {
    results.value = await api('/gov_suche', {
      params: { placename: query },
    })
  } catch (e) {
    error.value = e?.message || gettext.$gettext('Search failed.')
  } finally {
    loading.value = false
  }
}

function addName(name) {
  const sprache_id = findLanguageId(name.lang)
  if (!sprache_id || !name.value?.trim()) return

  emit('add', {
    sprache_id,
    text: name.value.trim(),
  })
}

function selectPlace(result) {
  emit('select-place', {
    gov_id: result.id,
    lon: result.position?.lon ?? '',
    lat: result.position?.lat ?? '',
  })
}

</script>

<template>
  <section class="mt-4">
    <h3 class="h6">{{ gettext.$gettext('GOV place search') }}</h3>

    <form class="input-group mb-3" @submit.prevent="search">
      <input
        v-model="placename"
        type="search"
        class="form-control"
        :placeholder="gettext.$gettext('Search GOV place name')"
        :aria-label="gettext.$gettext('Search GOV place name')"
      />
      <button
        type="submit"
        class="btn btn-outline-primary"
        :disabled="loading || !placename.trim()"
      >
        {{
          loading
            ? gettext.$gettext('Searching...')
            : gettext.$gettext('Search')
        }}
      </button>
    </form>

    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <p
      v-if="!loading && placename.trim() && results.length === 0 && !error"
      class="text-muted small"
    >
      {{ gettext.$gettext('No results found.') }}
    </p>

    <div v-for="result in results" :key="result.id" class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
            <strong>{{ result.id }}</strong>

            <div class="d-flex align-items-center gap-2">
                <small v-if="result.position" class="text-muted">
                {{ result.position.lat }}, {{ result.position.lon }}
                ({{ result.position.type }})
                </small>

                <button
                type="button"
                class="btn btn-sm btn-outline-primary"
                @click="selectPlace(result)"
                >
                {{ gettext.$gettext('Add') }}
                </button>
            </div>
        </div>

        <ul class="list-group">
          <li
            v-for="(name, index) in result.name"
            :key="`${result.id}-${name.lang}-${index}`"
            class="list-group-item d-flex justify-content-between align-items-center gap-2"
          >
            <span>
              {{ name.value }}
              <small class="text-muted">
                ({{ languageLabel(name.lang) }} · {{ name.lang || '?' }})
              </small>
            </span>

            <button
              type="button"
              class="btn btn-sm btn-outline-primary"
              :disabled="!findLanguageId(name.lang) || !name.value?.trim()"
              @click="addName(name)"
            >
              {{ gettext.$gettext('Add') }}
            </button>
          </li>
        </ul>

        <p v-if="!result.name?.length" class="text-muted small mb-0">
          {{ gettext.$gettext('No names available.') }}
        </p>
      </div>
    </div>
  </section>
</template>
