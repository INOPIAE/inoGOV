import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/theme.css'
import './assets/app.css'
import App from './App.vue'
import { createAppRouter } from './router'
import { createI18n } from './i18n'
import { setOtpSetupHandler, setUnauthorizedHandler } from './api'
import { useAuthStore } from './stores/auth'
import { useSettingsStore } from './stores/settings'

const app = createApp(App)
const pinia = createPinia()
const router = createAppRouter()

app.use(pinia)
app.use(createI18n())
app.use(router)

const auth = useAuthStore()
setUnauthorizedHandler(() => {
  auth.clear()
  router.push('/login')
})
setOtpSetupHandler(async () => {
  await auth.fetchMe().catch(() => {})
  router.push('/account')
})

await Promise.all([auth.init(), useSettingsStore().load().catch(() => {})])
app.mount('#app')
