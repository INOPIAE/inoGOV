<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import SideNav from './components/SideNav.vue'
import AppFooter from './components/AppFooter.vue'

const navOpen = ref(false)
useRouter().afterEach(() => (navOpen.value = false))
</script>

<template>
  <div class="app-shell">
    <AppHeader @toggle-nav="navOpen = !navOpen" />
    <SideNav :open="navOpen" />
    <main class="app-main">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>
