<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useErrors } from '../composables/useErrors'

const MAPS_URL = (import.meta.env.VITE_MAPS_URL || '/maps').replace(/\/$/, '')
const ZOOM_MIN = 0.1
const ZOOM_MAX = 4
const ZOOM_STEP = 1.25

const { $gettext } = useGettext()
const { errorText } = useErrors()
const route = useRoute()

const square = ref(null)
const state = ref('loading') // loading | ready | missing | error
const error = ref('')
const imageFailed = ref(false)
const zoom = ref(1)
const viewport = ref(null)

const image = computed(() => square.value.image)
const imageUrl = computed(() => `${MAPS_URL}/${encodeURIComponent(image.value.filename)}`)
const canvasStyle = computed(() => ({
  width: `${image.value.width_px * zoom.value}px`,
  height: `${image.value.height_px * zoom.value}px`,
}))
const highlightStyle = computed(() => {
  const { x1, y1, x2, y2 } = square.value.area
  const { width_px: w, height_px: h } = image.value
  return {
    left: `${(x1 / w) * 100}%`,
    top: `${(y1 / h) * 100}%`,
    width: `${((x2 - x1) / w) * 100}%`,
    height: `${((y2 - y1) / h) * 100}%`,
  }
})
const percent = computed(() => Math.round(zoom.value * 100))
const extent = computed(() => square.value.extent)

const clamp = (value) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, value))

// Zoom um die Mitte des sichtbaren Ausschnitts, damit der Betrachter nicht "wegspringt".
async function setZoom(next) {
  const view = viewport.value
  const centerX = (view.scrollLeft + view.clientWidth / 2) / zoom.value
  const centerY = (view.scrollTop + view.clientHeight / 2) / zoom.value
  zoom.value = clamp(next)
  await nextTick()
  view.scrollLeft = centerX * zoom.value - view.clientWidth / 2
  view.scrollTop = centerY * zoom.value - view.clientHeight / 2
}

async function centerOnSquare() {
  await nextTick()
  const view = viewport.value
  if (!view) return
  const { x1, y1, x2, y2 } = square.value.area
  view.scrollLeft = ((x1 + x2) / 2) * zoom.value - view.clientWidth / 2
  view.scrollTop = ((y1 + y2) / 2) * zoom.value - view.clientHeight / 2
}

const zoomIn = () => setZoom(zoom.value * ZOOM_STEP)
const zoomOut = () => setZoom(zoom.value / ZOOM_STEP)
const actualSize = async () => {
  zoom.value = 1
  await centerOnSquare()
}
const fitToWidth = async () => {
  const view = viewport.value
  zoom.value = clamp(view.clientWidth > 0 ? view.clientWidth / image.value.width_px : 0.5)
  await nextTick()
  view.scrollLeft = 0
}

function onWheel(event) {
  if (!event.ctrlKey) return
  event.preventDefault()
  setZoom(event.deltaY < 0 ? zoom.value * ZOOM_STEP : zoom.value / ZOOM_STEP)
}

onMounted(async () => {
  try {
    const { karte, koordinate } = route.params
    square.value = await api(`/maps/${encodeURIComponent(karte)}/${encodeURIComponent(koordinate)}`)
    state.value = 'ready'
    await centerOnSquare()
  } catch (e) {
    if (e.status === 404) {
      state.value = 'missing'
    } else {
      state.value = 'error'
      error.value = errorText(e)
    }
  }
})
</script>

<template>
  <div>
    <h1 class="h3 mb-3" data-test="title">
      {{ $gettext('Map "%{karte}", square %{koordinate}', { karte: route.params.karte, koordinate: route.params.koordinate }) }}
    </h1>

    <p v-if="state === 'loading'">{{ $gettext('Please wait...') }}</p>
    <div v-else-if="state === 'missing'" class="alert alert-warning" role="alert" data-test="missing">
      {{ $gettext('No map data is available for this square.') }}
    </div>
    <div v-else-if="state === 'error'" class="alert alert-danger" role="alert" data-test="error">{{ error }}</div>

    <template v-else>
      <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
        <div class="btn-group" role="group" :aria-label="$gettext('Zoom')">
          <button type="button" class="btn btn-outline-primary" data-test="zoom-out" :aria-label="$gettext('Zoom out')" @click="zoomOut">&minus;</button>
          <button type="button" class="btn btn-outline-primary" data-test="zoom-in" :aria-label="$gettext('Zoom in')" @click="zoomIn">+</button>
        </div>
        <button type="button" class="btn btn-outline-primary" data-test="actual" @click="actualSize">{{ $gettext('Actual size') }}</button>
        <button type="button" class="btn btn-outline-primary" data-test="fit" @click="fitToWidth">{{ $gettext('Fit to width') }}</button>
        <span class="text-muted" data-test="percent">{{ $gettext('Zoom: %{percent} %', { percent }) }}</span>
      </div>
      <p class="small text-muted mb-2" data-test="extent">
        {{
          $gettext('Longitude %{from} to %{to}, latitude %{latFrom} to %{latTo}', {
            from: extent.lon_from,
            to: extent.lon_to,
            latFrom: extent.lat_from,
            latTo: extent.lat_to,
          })
        }}
      </p>

      <div v-if="imageFailed" class="alert alert-danger" role="alert" data-test="image-failed">
        {{ $gettext('The map image could not be loaded.') }}
      </div>
      <div
        ref="viewport"
        class="map-viewport"
        tabindex="0"
        role="region"
        :aria-label="$gettext('Map view')"
        data-test="viewport"
        @wheel="onWheel"
      >
        <div class="map-canvas" :style="canvasStyle" data-test="canvas">
          <img
            :src="imageUrl"
            :alt="$gettext('Map image with the highlighted square %{koordinate}', { koordinate: square.koordinate })"
            draggable="false"
            @error="imageFailed = true"
          />
          <div class="map-highlight" :style="highlightStyle" data-test="highlight"></div>
        </div>
      </div>
    </template>
  </div>
</template>
