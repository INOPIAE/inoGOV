<script setup>
import { onMounted, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'
import { useErrors } from '../composables/useErrors'

const ROLES = ['admin', 'user']
const { $gettext } = useGettext()
const { errorText } = useErrors()
const auth = useAuthStore()

const users = ref([])
const message = ref('')
const error = ref('')
const invite = ref({ email: '' })
const editing = ref(null)

async function load() {
  try {
    users.value = await api('/users')
  } catch (e) {
    error.value = errorText(e)
  }
}

async function run(action, success) {
  message.value = error.value = ''
  try {
    await action()
    message.value = success
    await load()
  } catch (e) {
    error.value = errorText(e)
  }
}

const sendInvite = () =>
  run(async () => {
    await api('/users/invite', { method: 'POST', body: { email: invite.value.email } })
    invite.value = { email: '' }
  }, $gettext('Invitation sent.'))

const resetPassword = (u) =>
  run(() => api(`/users/${u.id}/reset-password`, { method: 'POST' }), $gettext('Email with a link has been sent.'))
const resetOtp = (u) =>
  run(() => api(`/users/${u.id}/reset-otp`, { method: 'POST' }), $gettext('Email with a link has been sent.'))

function edit(u) {
  editing.value = { ...u, roles: [...u.roles] }
}

const save = () =>
  run(async () => {
    const u = editing.value
    await api(`/users/${u.id}`, {
      method: 'PATCH',
      body: { email: u.email, first_name: u.first_name, last_name: u.last_name, active: u.active, blocked: u.blocked, roles: u.roles },
    })
    editing.value = null
  }, $gettext('Saved.'))

const toggleRole = (role, checked) => {
  const roles = new Set(editing.value.roles)
  checked ? roles.add(role) : roles.delete(role)
  editing.value.roles = [...roles]
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="h3 mb-3">{{ $gettext('User management') }}</h1>
    <div v-if="message" class="alert alert-success" role="status">{{ message }}</div>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <section class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('Invite new user') }}</h2>
        <form class="row g-2" @submit.prevent="sendInvite">
          <div class="col-12 col-md-9">
            <input v-model="invite.email" type="email" class="form-control" :placeholder="$gettext('Email address')" :aria-label="$gettext('Email address')" required />
          </div>
          <div class="col-12 col-md-3">
            <button class="btn btn-primary w-100" type="submit">{{ $gettext('Invite') }}</button>
          </div>
        </form>
      </div>
    </section>

    <section v-if="editing" class="card mb-4">
      <div class="card-body">
        <h2 class="h5">{{ $gettext('Edit user') }}: {{ editing.username }}</h2>
        <form class="row g-2" @submit.prevent="save">
          <div class="col-12 col-md-4"><input v-model="editing.email" type="email" class="form-control" :aria-label="$gettext('Email address')" required /></div>
          <div class="col-6 col-md-4"><input v-model="editing.first_name" class="form-control" :aria-label="$gettext('First name')" /></div>
          <div class="col-6 col-md-4"><input v-model="editing.last_name" class="form-control" :aria-label="$gettext('Last name')" /></div>
          <div class="col-12 d-flex flex-wrap gap-3">
            <div v-for="role in ROLES" :key="role" class="form-check">
              <input :id="`role-${role}`" class="form-check-input" type="checkbox" :checked="editing.roles.includes(role)" @change="toggleRole(role, $event.target.checked)" />
              <label class="form-check-label" :for="`role-${role}`">{{ role }}</label>
            </div>
            <div class="form-check">
              <input id="edit-active" v-model="editing.active" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="edit-active">{{ $gettext('Active') }}</label>
            </div>
            <div class="form-check">
              <input id="edit-blocked" v-model="editing.blocked" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="edit-blocked">{{ $gettext('Blocked') }}</label>
            </div>
          </div>
          <div class="col-12 d-flex gap-2">
            <button class="btn btn-primary" type="submit">{{ $gettext('Save') }}</button>
            <button class="btn btn-outline-secondary" type="button" @click="editing = null">{{ $gettext('Cancel') }}</button>
          </div>
        </form>
      </div>
    </section>

    <div class="table-responsive">
      <table class="table align-middle">
        <thead>
          <tr>
            <th>{{ $gettext('Username') }}</th>
            <th>{{ $gettext('Email address') }}</th>
            <th>{{ $gettext('Roles') }}</th>
            <th>{{ $gettext('Status') }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" data-test="user-row">
            <td>{{ u.pending ? '-' : u.username }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.roles.join(', ') }}</td>
            <td>
              <span v-if="u.pending" class="badge text-bg-info me-1">{{ $gettext('Invited') }}</span>
              <span v-if="!u.active" class="badge text-bg-secondary me-1">{{ $gettext('Inactive') }}</span>
              <span v-if="u.blocked" class="badge text-bg-danger me-1">{{ $gettext('Blocked') }}</span>
              <span v-if="u.otp_enabled" class="badge text-bg-success me-1">OTP</span>
            </td>
            <td class="text-end">
              <div class="d-flex flex-wrap justify-content-end gap-1">
                <button class="btn btn-sm btn-outline-primary" @click="edit(u)">{{ $gettext('Edit') }}</button>
                <button class="btn btn-sm btn-outline-secondary" @click="resetPassword(u)">
                  {{ u.pending ? $gettext('Resend invitation') : $gettext('Reset password') }}
                </button>
                <button v-if="!u.pending" class="btn btn-sm btn-outline-secondary" @click="resetOtp(u)">{{ $gettext('Reset OTP') }}</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="auth.user" class="text-muted small">{{ $gettext('Resetting sends the user an email with a link.') }}</p>
  </div>
</template>
