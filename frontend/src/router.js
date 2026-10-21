import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useSettingsStore } from './stores/settings'

export const routes = [
  { path: '/', name: 'home', component: () => import('./views/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('./views/LoginView.vue') },
  { path: '/map/:karte/:koordinate', name: 'map', component: () => import('./views/MapView.vue') },
  { path: '/forgot-password', component: () => import('./views/ForgotPasswordView.vue') },
  { path: '/reset-password', component: () => import('./views/ResetPasswordView.vue') },
  { path: '/setup-account', component: () => import('./views/SetupAccountView.vue') },
  { path: '/otp-setup', component: () => import('./views/OtpLinkView.vue') },
  { path: '/account', component: () => import('./views/AccountView.vue'), meta: { auth: true } },
  { path: '/users', component: () => import('./views/UsersView.vue'), meta: { auth: true, role: 'admin' } },
  { path: '/manage/orte', component: () => import('./views/ManageOrteView.vue'), meta: { auth: true, role: 'editor' } },
  { path: '/manage/kreise', component: () => import('./views/ManageKreiseView.vue'), meta: { auth: true, role: 'editor' } },
  { path: '/manage/karten', component: () => import('./views/ManageKartenView.vue'), meta: { auth: true, role: 'editor' } },
  { path: '/manage/imports', component: () => import('./views/ImportsView.vue'), meta: { auth: true, role: 'admin' } },
  { path: '/about', component: () => import('./views/InfoView.vue'), props: { page: 'about' } },
  { path: '/imprint', component: () => import('./views/InfoView.vue'), props: { page: 'imprint' } },
  { path: '/privacy', component: () => import('./views/InfoView.vue'), props: { page: 'privacy' } },
  { path: '/terms', component: () => import('./views/InfoView.vue'), props: { page: 'terms' } },
  { path: '/license', component: () => import('./views/InfoView.vue'), props: { page: 'license' } },
  { path: '/third-party-licenses', component: () => import('./views/InfoView.vue'), props: { page: 'tp_license' } },
  { path: '/statistics', component: () => import('./views/OrteStatisticsView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export function createAppRouter(history = createWebHistory()) {
  const router = createRouter({ history, routes })
  router.beforeEach((to) => {
    const auth = useAuthStore()
    // Admins ohne OTP dürfen nur die Einrichtung auf "Mein Konto" nutzen
    if (auth.otpSetupRequired) return to.path === '/account' ? true : '/account'
    const searchRequiresLogin = ['home', 'map'].includes(to.name) && !useSettingsStore().publicSearch
    if (!to.meta.auth && !searchRequiresLogin) return true
    if (!auth.isLoggedIn) return { path: '/login', query: { next: to.fullPath } }
    if (to.meta.role === 'admin' && !auth.isAdmin) return '/'
    if (to.meta.role === 'editor' && !auth.canEdit) return '/'
    return true
  })
  return router
}
