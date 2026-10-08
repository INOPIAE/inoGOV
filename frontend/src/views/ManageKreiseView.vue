<script setup>
import { computed, onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'
import { useSettingsStore } from '../stores/settings'
import NamesEditor from '../components/NamesEditor.vue'

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
const label = (kreis) => settings.pickName(kreis.namen, 'kreisname', language.value) || kreis.gov_id || '?'
const nameItems = computed(() => (form.value?.namen ?? []).map((n) => ({ id: n.id, sprache_id: n.sprache_id, text: n.kreisname })))

const empty = () => ({ id: null, gov_id: '', addition: '', comment: '', namen: [] })
const toForm = (k) => ({ ...k, gov_id: k.gov_id ?? '', addition: k.addition ?? '', comment: k.comment ?? '' })
const clean = (v) => (v === '' ? null : v)

async function guard(action) {
  message.value = error.value = ''
  try {
    await action()
  } catch (e) {
    error.value = errorText(e)
  }
}

const loadList = () =>
  guard(async () => {
    list.value = await api('/kreise', { params: { q: q.value.trim(), limit: 200 } })
  })

const refresh = async (id) => {
  form.value = toForm(await api(`/kreise/${id}`))
}

const save = () =>
  guard(async () => {
    const f = form.value
    const body = { gov_id: clean(f.gov_id), addition: clean(f.addition), comment: clean(f.comment) }
    const saved = f.id
      ? await api(`/kreise/${f.id}`, { method: 'PATCH', body })
      : await api('/kreise', { method: 'POST', body })
    form.value = toForm(saved)
    message.value = $gettext('Saved.')
    await loadList()
    await settings.loadKreise()
  })

const remove = () =>
  guard(async () => {
    if (!window.confirm($gettext('Really delete this district?'))) return
    await api(`/kreise/${form.value.id}`, { method: 'DELETE' })
    form.value = null
    await loadList()
    await settings.loadKreise()
  })

const addName = ({ sprache_id, text }) =>
  guard(async () => {
    await api(`/kreise/${form.value.id}/namen`, { method: 'POST', body: { sprache_id, kreisname: text } })
    await refresh(form.value.id)
    await settings.loadKreise()
  })

const removeName = (nameId) =>
  guard(async () => {
    await api(`/kreise/${form.value.id}/namen/${nameId}`, { method: 'DELETE' })
    await refresh(form.value.id)
    await settings.loadKreise()
  })

onMounted(async () => {
  await guard(() => settings.loadReference())
  await loadList()
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Districts') }}</h1>
    <div v-if="message" class="alert alert-success" role="status">{{ message }}</div>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <div class="row g-4">
      <div class="col-12 col-lg-5">
        <form class="input-group mb-2" @submit.prevent="loadList">
          <input v-model="q" type="search" class="form-control" :placeholder="$gettext('District name')" :aria-label="$gettext('District name')" />
          <button class="btn btn-outline-primary" type="submit">{{ $gettext('Search') }}</button>
        </form>
        <button class="btn btn-primary mb-2" @click="form = empty()">{{ $gettext('New district') }}</button>
        <div class="list-group">
          <button
            v-for="kreis in list"
            :key="kreis.id"
            type="button"
            class="list-group-item list-group-item-action"
            :class="{ active: form?.id === kreis.id }"
            data-test="list-item"
            @click="form = toForm(kreis)"
          >
            {{ label(kreis) }}
          </button>
        </div>
      </div>

      <div class="col-12 col-lg-7">
        <form v-if="form" class="card card-body" @submit.prevent="save">
          <div class="mb-2">
            <label class="form-label" for="gov">GOV-ID</label>
            <input id="gov" v-model="form.gov_id" class="form-control" maxlength="20" />
          </div>
          <div class="mb-2">
            <label class="form-label" for="addition">{{ $gettext('Addition') }}</label>
            <input id="addition" v-model="form.addition" class="form-control" maxlength="255" />
          </div>
          <div class="mb-3">
            <label class="form-label" for="comment">{{ $gettext('Comment') }}</label>
            <textarea id="comment" v-model="form.comment" class="form-control" rows="2"></textarea>
          </div>
          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-primary" type="submit">{{ $gettext('Save') }}</button>
            <button v-if="form.id" class="btn btn-outline-danger" type="button" @click="remove">{{ $gettext('Delete') }}</button>
          </div>
          <NamesEditor v-if="form.id" :items="nameItems" :label="$gettext('District names')" @add="addName" @remove="removeName" />
          <p v-else class="text-muted small mb-0">{{ $gettext('Save the district first, then add names.') }}</p>
        </form>
      </div>
    </div>
  </div>
</template>
