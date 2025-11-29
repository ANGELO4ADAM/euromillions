<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">EuroDream</p>
        <h1>Expérience miroir avec l'arsenal EOP</h1>
        <p class="muted">Stratégies, backtesting et favoris alignés sur l'univers EuroMillions pour un pilotage bicéphale.</p>
      </div>
      <div class="chips">
        <span class="chip">Vue dédiée</span>
        <span class="chip secondary">Monte Carlo + Fibo</span>
        <span class="chip ghost">Parité Romignon</span>
      </div>
    </header>

    <div class="grid">
      <div class="card">
        <div class="card-title">Tirage récent EuroDream</div>
        <p class="muted">Synchronisé sur les mêmes APIs avec isolation par jeu.</p>
        <div class="pill-row">
          <span v-for="n in lastDraw.numbers" :key="`n-${n}`" class="pill">{{ n }}</span>
          <span v-for="s in lastDraw.stars" :key="`s-${s}`" class="pill star">{{ s }}</span>
        </div>
        <p class="muted" v-if="!lastDraw.numbers.length">Aucun tirage enregistré pour le moment.</p>
      </div>

      <div class="card">
        <div class="card-title">Générateur Monte Carlo + Fibonacci</div>
        <p class="muted">200 itérations pondérées par Fibo pour extraire les combos les plus stables.</p>
        <div class="pill-row">
          <span v-for="n in generated.numbers" :key="`gn-${n}`" class="pill">{{ n }}</span>
          <span v-for="s in generated.stars" :key="`gs-${s}`" class="pill star">{{ s }}</span>
        </div>
        <div class="meta">Score: {{ generated.confidence_score }} · {{ generated.method_used }}</div>
        <button class="ghost-btn" @click="runMonteCarlo" :disabled="loading">
          {{ loading ? 'Calcul...' : 'Relancer la stratégie' }}
        </button>
      </div>

      <div class="card">
        <div class="card-title">Répartition (analytics)</div>
        <p class="muted">Fréquences des numéros & étoiles sur le scope EuroDream.</p>
        <div class="analytics">
          <div class="analytics-row" v-for="chunk in analyticsChunks" :key="chunk.label">
            <div class="analytics-label">{{ chunk.label }}</div>
            <div class="analytics-values">
              <span v-for="item in chunk.values" :key="item.label" class="analytic-pill">
                {{ item.label }}<small>{{ item.count }}</small>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchAnalytics, fetchDraws, generateMonteCarloFibo } from '../apiService'

const lastDraw = ref({ numbers: [], stars: [] })
const generated = ref({ numbers: [], stars: [], confidence_score: 0, method_used: 'monte_carlo_fibo' })
const analytics = ref({ numbers: {}, stars: {} })
const loading = ref(false)

const token = localStorage.getItem('token')

const loadDraw = async () => {
  if (!token) return
  const { data } = await fetchDraws(token, 'eurodream')
  lastDraw.value = data
}

const runMonteCarlo = async () => {
  if (!token) return
  loading.value = true
  try {
    const { data } = await generateMonteCarloFibo(token, 'eurodream')
    generated.value = data
  } finally {
    loading.value = false
  }
}

const loadAnalytics = async () => {
  if (!token) return
  const { data } = await fetchAnalytics(token, 'eurodream')
  analytics.value = data
}

const analyticsChunks = computed(() => {
  const entries = Object.entries(analytics.value.numbers || {})
  const chunks = []
  for (let i = 0; i < entries.length; i += 10) {
    const slice = entries.slice(i, i + 10).map(([label, count]) => ({ label, count }))
    chunks.push({ label: `Numéros ${i + 1}-${i + slice.length}`, values: slice })
  }
  if (analytics.value.stars) {
    chunks.push({
      label: 'Étoiles',
      values: Object.entries(analytics.value.stars).map(([label, count]) => ({ label: `★${label}`, count }))
    })
  }
  return chunks
})

onMounted(async () => {
  await loadDraw()
  await runMonteCarlo()
  await loadAnalytics()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--accent);
  margin: 0;
}

.chips {
  display: flex;
  gap: 0.5rem;
}

.chip {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 0.85rem;
}

.chip.secondary {
  background: rgba(99,102,241,0.15);
  color: var(--accent);
  border: 1px solid var(--accent);
}

.chip.ghost {
  background: rgba(56,189,248,0.15);
  color: rgb(14,165,233);
  border: 1px dashed rgba(56,189,248,0.5);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 1rem;
  border: 1px solid var(--border-subtle);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.pill {
  padding: 0.35rem 0.55rem;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.14);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  font-weight: 600;
}

.pill.star {
  background: rgba(255, 206, 86, 0.16);
  border-color: rgba(255, 206, 86, 0.6);
}

.meta {
  margin-top: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.ghost-btn {
  margin-top: 0.75rem;
  padding: 0.6rem 0.9rem;
  border-radius: 12px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  transition: all 0.2s ease;
}

.ghost-btn:hover {
  background: rgba(99, 102, 241, 0.1);
}

.ghost-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analytics {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 260px;
  overflow: auto;
}

.analytics-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.analytics-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.analytic-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.5rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  font-size: 0.9rem;
}

.analytic-pill small {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.muted {
  color: var(--text-muted);
  margin: 0 0 0.75rem;
}

.placeholder {
  padding: 0.75rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.04);
  color: var(--text-muted);
  text-align: center;
  border: 1px dashed var(--border-subtle);
}
</style>
