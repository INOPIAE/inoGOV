<script setup>
import { onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'

const { $gettext } = useGettext()
const { errorText } = useErrors()

const imports = ref([])
const key = ref('')
const file = ref(null)
const busy = ref(false)
const report = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    imports.value = await api('/imports')
    key.value = imports.value[0]?.key ?? ''
  } catch (e) {
    error.value = errorText(e)
  }
})

function describe(importKey) {
  if (importKey === 'ImportLueck') {
    return $gettext(
      'CSV file with a header row and three columns: Polish place name, Polish district name, coordinate. Every row creates a new place with a reference to the map "Lück".',
    )
  }
  return ''
}

function rowError(item) {
  switch (item.code) {
    case 'columns':
      return $gettext('Fewer than 3 columns.')
    case 'empty_place':
      return $gettext('Place name is missing.')
    case 'empty_district':
      return $gettext('District name is missing.')
    case 'empty_coordinate':
      return $gettext('Coordinate is missing.')
    case 'place_too_long':
      return $gettext('Place name is longer than 255 characters.')
    case 'district_too_long':
      return $gettext('District name is longer than 50 characters.')
    case 'coordinate_too_long':
      return $gettext('Coordinate is longer than 2 characters.')
    case 'unexpected':
      return $gettext('Unexpected error while saving this row.')
    default:
      return item.message
  }
}

function onFile(event) {
  file.value = event.target.files?.[0] ?? null
}

async function start() {
  if (!file.value || !key.value || busy.value) return
  busy.value = true
  error.value = ''
  report.value = null
  try {
    const form = new FormData()
    form.append('file', file.value)
    report.value = await api(`/imports/${encodeURIComponent(key.value)}`, { method: 'POST', body: form })
  } catch (e) {
    if (e.status === 413) error.value = $gettext('The file is too large.')
    else if (e.status === 422 && e.detail === 'no_polish')
      error.value = $gettext('The Polish language is missing in the language table.')
    else error.value = errorText(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('Imports') }}</h1>
    <div v-if="error" class="alert alert-danger" role="alert" data-test="import-error">{{ error }}</div>

    <section class="card mb-4">
      <div class="card-body">
        <form @submit.prevent="start">
          <div class="mb-3">
            <label class="form-label" for="import-key">{{ $gettext('Import') }}</label>
            <select id="import-key" v-model="key" class="form-select">
              <option v-for="item in imports" :key="item.key" :value="item.key">{{ item.key }}</option>
            </select>
            <div v-if="key" class="form-text" data-test="description">{{ describe(key) }}</div>
          </div>
          <div class="mb-3">
            <label class="form-label" for="import-file">{{ $gettext('CSV file') }}</label>
            <input id="import-file" type="file" class="form-control" accept=".csv,text/csv,text/plain" @change="onFile" />
            <div class="form-text">{{ $gettext('Rows with errors are skipped and listed below. Duplicates are not checked.') }}</div>
          </div>
          <button class="btn btn-primary" type="submit" :disabled="!file || !key || busy">
            {{ busy ? $gettext('Please wait...') : $gettext('Start import') }}
          </button>
        </form>
      </div>
    </section>

    <section v-if="report" data-test="report">
      <div class="alert" :class="report.failed ? 'alert-warning' : 'alert-success'" role="status" data-test="summary">
        {{ $gettext('%{imported} of %{total} rows imported, %{failed} with errors.', { imported: report.imported, total: report.total, failed: report.failed }) }}
      </div>

      <div v-if="report.created_kreise.length" class="card mb-3" data-test="created">
        <div class="card-body">
          <h2 class="h5">{{ $gettext('New districts created (Polish name)') }}</h2>
          <ul class="mb-0">
            <li v-for="kreis in report.created_kreise" :key="kreis.id">{{ kreis.name }}</li>
          </ul>
        </div>
      </div>

      <div v-if="report.errors.length" class="card mb-3" data-test="errors">
        <div class="card-body">
          <h2 class="h5">{{ $gettext('Errors') }}</h2>
          <div class="table-responsive">
            <table class="table table-sm align-middle mb-0">
              <thead>
                <tr>
                  <th>{{ $gettext('Line') }}</th>
                  <th>{{ $gettext('Reason') }}</th>
                  <th>{{ $gettext('Row content') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in report.errors" :key="item.line" data-test="error-row">
                  <td>{{ item.line }}</td>
                  <td>{{ rowError(item) }}</td>
                  <td class="text-break">{{ item.values.join('; ') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <p v-if="report.archived_as" class="text-muted small" data-test="archived">
        {{ $gettext('File archived as %{name}.', { name: report.archived_as }) }}
      </p>
      <div v-if="report.archive_failed" class="alert alert-warning" role="alert" data-test="archive-failed">
        {{ $gettext('The file could not be archived. The import itself was saved.') }}
      </div>
    </section>
  </div>
</template>
