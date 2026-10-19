
<script setup>
import { onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'

const gettext = useGettext()
const { errorText } = useErrors()

const statistics = ref(null)
const loading = ref(false)
const error = ref('')

async function loadStatistics() {
  loading.value = true
  error.value = ''

  try {
    statistics.value = await api('/orte/statistics/')
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadStatistics)
</script>

<template>
  <div>
    <h1 class="h3 mb-3">
      {{ gettext.$gettext('Place statistics') }}
    </h1>

    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-if="loading" class="text-muted">
      {{ gettext.$gettext('Loading statistics...') }}
    </div>

    <template v-else-if="statistics">
      <div class="row g-3">
        <div class="col-12 col-md-3">
          <div class="card h-100">
            <div class="card-body">
              <h2 class="h6 text-muted">
                {{ gettext.$gettext('Places') }}
              </h2>
              <p class="display-6 mb-0">
                {{ statistics.total }}
              </p>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="card h-100">
            <div class="card-body">
              <h2 class="h6 text-muted">
                {{ gettext.$gettext('Places with GOV-ID') }}
              </h2>
              <p class="display-6 mb-0">
                {{ statistics.gov }}
              </p>
              <small v-if="statistics.total > 0" class="text-muted">
                {{ (statistics.gov / statistics.total * 100).toLocaleString(
                  gettext.current,
                  { maximumFractionDigits: 1 }
                ) }} %
              </small>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="card h-100">
            <div class="card-body">
              <h2 class="h6 text-muted">
                {{ gettext.$gettext('Places with coordinates') }}
              </h2>
              <p class="display-6 mb-0">
                {{ statistics.geo }}
              </p>
              <small v-if="statistics.total > 0" class="text-muted">
                {{ (statistics.geo / statistics.total * 100).toLocaleString(
                  gettext.current,
                  { maximumFractionDigits: 1 }
                ) }} %
              </small>
            </div>
          </div>
        </div>

        <div class="col-12 col-md-3">
          <div class="card h-100">
            <div class="card-body">
              <h2 class="h6 text-muted">
                {{ gettext.$gettext('Places with coordinates not found') }}
              </h2>
              <p class="display-6 mb-0">
                {{ statistics.not_found }}
              </p>
              <small v-if="statistics.total > 0" class="text-muted">
                {{ (statistics.not_found / statistics.total * 100).toLocaleString(
                  gettext.current,
                  { maximumFractionDigits: 1 }
                ) }} %
              </small>
            </div>
          </div>
        </div>
      </div>

      <button
        type="button"
        class="btn btn-outline-primary mt-3"
        :disabled="loading"
        @click="loadStatistics"
      >
        {{ gettext.$gettext('Refresh') }}
      </button>
    </template>
  </div>
</template>
