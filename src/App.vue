<template>
  <div class="app" :class="theme">
    <header class="topbar" v-if="showNav">
      <div class="logo">EOP</div>
      <nav class="nav">
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path" class="nav-link">
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="topbar-right">
        <div class="user-pill" title="Utilisateur courant">{{ userName }}</div>
        <button class="mode-toggle" @click="toggleTheme">{{ theme === 'dark' ? 'Light' : 'Dark' }}</button>
      </div>
    </header>
    <main class="content" :class="{ 'full-height': !showNav }">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { universes } from './universes'

const route = useRoute()
const theme = ref('dark')
const userName = ref('Invité')

const menu = [
  ...universes.map((u) => ({ path: u.basePath, label: u.label })),
  { path: '/generateur', label: 'Générateur' },
  { path: '/backtesting', label: 'Backtesting' },
  { path: '/favoris', label: 'Favoris' },
  { path: '/campagnes', label: 'Campagnes' },
  { path: '/rapport', label: 'Rapport' }
]

const showNav = computed(() => route.path !== '/')

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}
</script>
