<script setup>
import { onMounted, ref } from 'vue'
import QRCode from 'qrcode'
import { useGettext } from 'vue3-gettext'
import { useErrors } from '../composables/useErrors'

// start() liefert { secret, uri, setup_token }, confirm(setupToken, code) schließt die Einrichtung ab.
const props = defineProps({ start: Function, confirm: Function })
const emit = defineEmits(['done'])

const { $gettext } = useGettext()
const { errorText } = useErrors()
const setup = ref(null)
const qr = ref('')
const code = ref('')
const error = ref('')
const copied = ref(false)

onMounted(async () => {
  try {
    setup.value = await props.start()
    qr.value = await QRCode.toDataURL(setup.value.uri, { margin: 1, width: 200 })
  } catch (e) {
    error.value = errorText(e)
  }
})

async function copySecret() {
  await navigator.clipboard.writeText(setup.value.secret)
  copied.value = true
}

async function submit() {
  error.value = ''
  try {
    await props.confirm(setup.value.setup_token, code.value.trim())
    emit('done')
  } catch (e) {
    error.value = e?.status === 400 ? $gettext('The code is wrong or the setup has expired.') : errorText(e)
  }
}
</script>

<template>
  <div>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="setup">
      <p>{{ $gettext('Scan the QR code with your authenticator app or enter the key manually.') }}</p>
      <img v-if="qr" :src="qr" class="qr-image mb-3 d-block" :alt="$gettext('QR code for the authenticator app')" />
      <div class="input-group mb-3">
        <input class="form-control secret-text" readonly :value="setup.secret" :aria-label="$gettext('Secret key')" />
        <button type="button" class="btn btn-outline-primary" @click="copySecret">
          {{ copied ? $gettext('Copied') : $gettext('Copy') }}
        </button>
      </div>
      <form @submit.prevent="submit">
        <label class="form-label" for="otp-confirm">{{ $gettext('Enter a new code from the app to finish the setup') }}</label>
        <div class="input-group">
          <input
            id="otp-confirm"
            v-model="code"
            class="form-control"
            inputmode="numeric"
            autocomplete="one-time-code"
            required
          />
          <button class="btn btn-primary" type="submit">{{ $gettext('Confirm') }}</button>
        </div>
      </form>
    </div>
  </div>
</template>
