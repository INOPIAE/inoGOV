<script setup>
import { computed, onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'
import { useSettingsStore } from '../stores/settings'
import NamesEditor from '../components/NamesEditor.vue'
import GovSuche from '../components/GovSuche.vue'

const gettext = useGettext()
const { $gettext } = gettext
const { errorText } = useErrors()
const settings = useSettingsStore()

const q = ref('')
const list = ref([])
const form = ref(null)
const message = ref('')
const error = ref('')

const language = computed(() => gettext.current)
const label = (ort) => settings.pickName(ort.namen, 'ortsname', language.value) || ort.gov_id || '?'
const nameItems = computed(() => (form.value?.namen ?? []).map((n) => ({ id: n.id, sprache_id: n.sprache_id, text: n.ortsname })))

const empty = () => ({ id: null, gov_id: '', kreis_id: '', lat: '', lon: '', addition: '', comment: '', namen: [] })
const toForm = (ort) => ({
  ...ort,
  gov_id: ort.gov_id ?? '',
  kreis_id: ort.kreis_id ?? '',
  lat: ort.lat ?? '',
  lon: ort.lon ?? '',
  addition: ort.addition ?? '',
  comment: ort.comment ?? '',
})
const clean = (v) => (v === '' ? null : v)

async function guard(action) {
  message.value = error.value = ''
  try {
    await action()
  } catch (e) {
    error.value = errorText(e)
  }
}

const loadList = () => guard(async () => (list.value = await api('/orte', { params: { q: q.value.trim(), limit: 50 } })))

const refresh = async (id) => {
  form.value = toForm(await api(`/orte/${id}`))
}

const save = () =>
  guard(async () => {
    const f = form.value
    const body = {
      gov_id: clean(f.gov_id),
      kreis_id: clean(f.kreis_id),
      lat: clean(f.lat),
      lon: clean(f.lon),
      addition: clean(f.addition),
      comment: clean(f.comment),
    }
    const saved = f.id
      ? await api(`/orte/${f.id}`, { method: 'PATCH', body })
      : await api('/orte', { method: 'POST', body })
    form.value = toForm(saved)
    message.value = $gettext('Saved.')
    list.value = await api('/orte', { params: { q: q.value.trim(), limit: 50 } })
  })

const remove = () =>
  guard(async () => {
    if (!window.confirm($gettext('Really delete this place?'))) return
    await api(`/orte/${form.value.id}`, { method: 'DELETE' })
    form.value = null
    await loadList()
  })

const addName = ({ sprache_id, text }) =>
  guard(async () => {
    await api(`/orte/${form.value.id}/namen`, { method: 'POST', body: { sprache_id, ortsname: text } })
    await refresh(form.value.id)
  })

const removeName = (nameId) =>
  guard(async () => {
    await api(`/orte/${form.value.id}/namen/${nameId}`, { method: 'DELETE' })
    await refresh(form.value.id)
  })

const addGovPlace = (data) =>
  guard(async () => {
    if (!form.value) return

    form.value.gov_id = data.gov_id
    form.value.lon = data.lon
    form.value.lat = data.lat

    await save()
})

onMounted(async () => {
  await guard(() => settings.loadReference())
  await loadList()
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Places') }}</h1>
    <div v-if="message" class="alert alert-success" role="status">{{ message }}</div>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <div class="row g-4">
      <div class="col-12 col-lg-5">
        <form class="input-group mb-2" @submit.prevent="loadList">
          <input v-model="q" type="search" class="form-control" :placeholder="$gettext('Place name')" :aria-label="$gettext('Place name')" />
          <button class="btn btn-outline-primary" type="submit">{{ $gettext('Search') }}</button>
        </form>
        <button class="btn btn-primary mb-2" @click="form = empty()">{{ $gettext('New place') }}</button>
        <div class="list-group">
          <button
            v-for="ort in list"
            :key="ort.id"
            type="button"
            class="list-group-item list-group-item-action"
            :class="{ active: form?.id === ort.id }"
            data-test="list-item"
            @click="form = toForm(ort)"
          >
            {{ label(ort) }} <small v-if="ort.gov_id">({{ ort.gov_id }})</small>
          </button>
        </div>
      </div>

      <div class="col-12 col-lg-7">
        <form v-if="form" class="card card-body" @submit.prevent="save">
          <div class="row g-2 mb-2">
            <div class="col-12 col-sm-6">
              <label class="form-label" for="gov">GOV-ID</label>
              <input id="gov" v-model="form.gov_id" class="form-control" maxlength="20" />
            </div>
            <div class="col-12 col-sm-6">
              <label class="form-label" for="kreis">{{ $gettext('District') }}</label>
              <select id="kreis" v-model="form.kreis_id" class="form-select">
                <option value="">-</option>
                <option v-for="k in settings.kreise" :key="k.id" :value="k.id">{{ settings.pickName(k.namen, 'kreisname', language) || k.gov_id }}</option>
              </select>
            </div>
            <div class="col-6">
              <label class="form-label" for="lat">{{ $gettext('Latitude') }}</label>
              <input id="lat" v-model="form.lat" class="form-control" inputmode="decimal" />
            </div>
            <div class="col-6">
              <label class="form-label" for="lon">{{ $gettext('Longitude') }}</label>
              <input id="lon" v-model="form.lon" class="form-control" inputmode="decimal" />
            </div>
            <div class="col-12">
              <label class="form-label" for="addition">{{ $gettext('Addition') }}</label>
              <input id="addition" v-model="form.addition" class="form-control" maxlength="255" />
            </div>
            <div class="col-12">
              <label class="form-label" for="comment">{{ $gettext('Comment') }}</label>
              <textarea id="comment" v-model="form.comment" class="form-control" rows="2"></textarea>
            </div>
          </div>
          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-primary" type="submit">{{ $gettext('Save') }}</button>
            <button v-if="form.id" class="btn btn-outline-danger" type="button" @click="remove">{{ $gettext('Delete') }}</button>
          </div>
          <NamesEditor
            v-if="form.id"
            :items="nameItems"
            :label="$gettext('Place names')"
            @add="addName"
            @remove="removeName"
          />

          <GovSuche
            v-if="form.id"
            @add="addName"
            @select-place="addGovPlace"
          />

          <p v-else class="text-muted small mb-0">{{ $gettext('Save the place first, then add names.') }}</p>
        </form>
      </div>
    </div>
  </div>
</template>
