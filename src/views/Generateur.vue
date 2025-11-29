<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Moteur de stratégies</p>
        <h1>Générateur multi-stratégies</h1>
        <p class="subtitle">Comparez, sélectionnez et lancez les principales stratégies validées (8+).</p>
      </div>
      <div class="pill pill-success">Univers : {{ selectedGameLabel }}</div>
    </header>

    <section class="card">
      <div class="section-header">
        <div>
          <h3>Choix de l'univers</h3>
          <p class="muted">EuroMillions ou EuroDream, chaque stratégie respecte le profil de jeu.</p>
        </div>
        <select v-model="selectedGame" class="select">
          <option v-for="universe in universes" :key="universe.key" :value="universe.key">
            {{ universe.label }}
          </option>
        </select>
      </div>
    </section>

    <section class="card">
      <div class="section-header">
        <div>
          <h3>Menu des stratégies</h3>
          <p class="muted">Sélectionnez une stratégie validée puis lancez la génération.</p>
        </div>
        <div class="pill pill-info">{{ strategies.length }} stratégies</div>
      </div>

      <div class="strategy-grid">
        <article
          v-for="strategy in strategies"
          :key="strategy.key"
          class="strategy-card"
          :class="{ active: strategy.key === selectedStrategy }"
          @click="selectedStrategy = strategy.key"
        >
          <div class="strategy-head">
            <span class="badge" :class="strategy.badgeClass">{{ strategy.short }}</span>
            <span class="pill pill-ghost">{{ strategy.category }}</span>
          </div>
          <h4>{{ strategy.label }}</h4>
          <p class="muted">{{ strategy.description }}</p>
          <div class="strategy-footer">
            <span class="meta">Score base {{ strategy.score }}/100</span>
            <span class="meta">{{ strategy.intent }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="card">
      <div class="section-header">
        <div>
          <h3>Exécution</h3>
          <p class="muted">Lancement instantané, validation du jeu cible et rendu détaillé.</p>
        </div>
        <button class="button-primary" :disabled="loading" @click="runGeneration">
          {{ loading ? 'Génération…' : 'Lancer la stratégie' }}
        </button>
      </div>

      <div class="results-panel" v-if="result">
        <div class="result-header">
          <div>
            <p class="eyebrow">{{ result.method_used }} • {{ selectedGameLabel }}</p>
            <h4>Grille générée</h4>
          </div>
          <div class="confidence">{{ Math.round(result.confidence_score * 100) }}% confiance</div>
        </div>
        <div class="chips-row">
          <span class="chip" v-for="n in result.numbers" :key="`n-${n}`">{{ n }}</span>
        </div>
        <div class="chips-row stars">
          <span class="chip star" v-for="s in result.stars" :key="`s-${s}`">★ {{ s }}</span>
        </div>
        <p class="muted">{{ result.explanation }}</p>
      </div>

      <div class="alert" v-if="error">{{ error }}</div>
      <div class="info-grid">
        <div class="info-card">
          <h5>Prérequis</h5>
          <p class="muted">Assurez-vous d'être authentifié pour exécuter les stratégies sécurisées.</p>
        </div>
        <div class="info-card">
          <h5>Monte Carlo Fibo</h5>
          <p class="muted">200 itérations pondérées par Fibonacci, disponible dans les 2 univers.</p>
        </div>
        <div class="info-card">
          <h5>Audit</h5>
          <p class="muted">Consultez /strategies/report pour suivre le statut de chaque implémentation.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

import { generateGrid } from '../apiService'
import { universes } from '../universes'

const strategies = [
  {
    key: 'meta_ia',
    label: 'Meta IA',
    short: 'META',
    category: 'Fusion',
    description: 'Fusion multi-profils, pondération dynamique et filtrage des écarts.',
    score: 72,
    intent: 'Multi-IA',
    badgeClass: 'badge-meta'
  },
  {
    key: 'fibonacci_inverse',
    label: 'Fibonacci Inversé',
    short: 'FIBO',
    category: 'Analytique',
    description: 'Projection par écarts et séquence Fibonacci inversée.',
    score: 65,
    intent: 'Écarts',
    badgeClass: 'badge-analytique'
  },
  {
    key: 'mcc',
    label: 'Monte-Carlo Combinatoire',
    short: 'MCC',
    category: 'Simulation',
    description: 'Simulation combinatoire pour extraire paires et noyaux.',
    score: 70,
    intent: 'Simulation',
    badgeClass: 'badge-simu'
  },
  {
    key: 'xgboost',
    label: 'XGBoost',
    short: 'XGB',
    category: 'ML',
    description: 'Gradient boosting supervisé sur historiques préparés.',
    score: 68,
    intent: 'ML',
    badgeClass: 'badge-ml'
  },
  {
    key: '3gs',
    label: '3GS',
    short: '3GS',
    category: 'Glissant',
    description: 'Stratégie glissante multi-fenêtres pour équilibrer les écarts.',
    score: 60,
    intent: 'Glissant',
    badgeClass: 'badge-glissant'
  },
  {
    key: 'spectre',
    label: 'Spectre AI',
    short: 'SPC',
    category: 'Pondération',
    description: 'Pondération automatique via sonar et spectres de fréquence.',
    score: 64,
    intent: 'Sonar',
    badgeClass: 'badge-pond'
  },
  {
    key: 'timeline_ai',
    label: 'Timeline AI',
    short: 'TLA',
    category: 'Simulation',
    description: 'Fenêtre figée -20 tirages et reprise jour par jour.',
    score: 62,
    intent: 'Timeline',
    badgeClass: 'badge-simu'
  },
  {
    key: 'echo_ecarts',
    label: "Echo des Écarts",
    short: 'ECHO',
    category: 'Écarts',
    description: 'Reflets d’écarts pour projeter les tendances et cassures.',
    score: 58,
    intent: 'Écarts',
    badgeClass: 'badge-analytique'
  },
  {
    key: 'monte_carlo_fibo',
    label: 'Monte-Carlo Fibo (200 itérations)',
    short: 'MCF',
    category: 'Hybride',
    description: 'Monte Carlo + pondération Fibonacci sur 200 runs pour extraire le meilleur noyau.',
    score: 76,
    intent: 'Hybride',
    badgeClass: 'badge-hybride'
  }
]

const selectedStrategy = ref(strategies[0].key)
const selectedGame = ref(universes[0].key)
const loading = ref(false)
const error = ref('')
const result = ref(null)

const selectedGameLabel = computed(() => universes.find((u) => u.key === selectedGame.value)?.label || 'Inconnu')

const runGeneration = async () => {
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const token = localStorage.getItem('token') || undefined
    const { data } = await generateGrid(selectedStrategy.value, token, selectedGame.value)
    result.value = data
  } catch (err) {
    error.value = err?.response?.data?.error || 'Impossible de lancer la stratégie. Vérifiez votre authentification.'
  } finally {
    loading.value = false
  }
}
</script>
