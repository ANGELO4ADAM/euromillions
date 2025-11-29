<template>
  <div class="card-grid">
    <section class="card span-2">
      <header class="card-header">
        <div>
          <p class="eyebrow">Vue Dashboard</p>
          <h3>Survol opérationnel</h3>
          <p class="muted">État synthétique du backend, des jeux et des stratégies.</p>
        </div>
        <button class="ghost" @click="refresh" :disabled="loading">
          {{ loading ? 'Actualisation…' : 'Rafraîchir' }}
        </button>
      </header>

      <div class="status-grid" v-if="!error">
        <div class="pill" :class="payload?.status === 'ok' ? 'pill-success' : 'pill-warn'">
          <strong>API</strong>
          <span>{{ payload?.status === 'ok' ? 'Opérationnel' : 'Dégradé' }}</span>
        </div>
        <div class="pill" v-if="payload?.db">
          <strong>DB</strong>
          <span>{{ payload.db.status }}</span>
        </div>
        <div class="pill" v-for="game in payload?.games || []" :key="game.key">
          <strong>{{ game.label }}</strong>
          <span>{{ game.numbers_count || game.numbers }} numéros / {{ game.stars_count || game.stars }} étoiles</span>
        </div>
        <div class="pill" v-if="payload?.strategies">
          <strong>Stratégies</strong>
          <span>{{ payload.strategies.length }} actives</span>
        </div>
      </div>

      <div class="table" v-if="payload?.db?.counts">
        <div class="table-row table-head">
          <span>Ressource</span>
          <span>Volume</span>
        </div>
        <div class="table-row" v-for="(count, key) in payload.db.counts" :key="key">
          <span>{{ key }}</span>
          <span>{{ count === null ? 'N/A' : count }}</span>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section class="card">
      <h3>Progression des campagnes</h3>
      <p>Suivi simplifié des campagnes en cours et récentes.</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchHealth } from '../apiService'

const loading = ref(true)
const error = ref(null)
const payload = ref(null)

const refresh = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await fetchHealth()
    payload.value = data
  } catch (err) {
    error.value = 'Impossible de récupérer le statut. Vérifiez le backend.'
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>
