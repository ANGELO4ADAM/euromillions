<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Tableau de bord</p>
        <h1>Rapport global</h1>
        <p class="muted">Panorama des fonctionnalités livrées et de l'état opérationnel.</p>
      </div>
      <div class="snapshot">
        <div class="pill success">Stable</div>
        <div class="pill ghost">Mis à jour</div>
      </div>
    </header>

    <div v-if="error" class="card error">{{ error }}</div>
    <div v-else-if="loading" class="card">Chargement du rapport...</div>
    <div v-else class="cards-grid">
      <div class="card stat" v-for="card in statCards" :key="card.label">
        <p class="muted">{{ card.label }}</p>
        <h2>{{ card.value }}</h2>
        <p class="muted">{{ card.subtitle }}</p>
      </div>
    </div>

    <div class="timeline card" v-if="!loading && !error">
      <header class="card-header">
        <div>
          <p class="eyebrow">Historique</p>
          <h3>Fonctionnalités de A à Z</h3>
        </div>
        <span class="muted">{{ history.length }} items</span>
      </header>
      <ul class="timeline-list">
        <li v-for="item in history" :key="item.title" class="timeline-item">
          <div class="badge" :data-area="item.area">{{ item.area }}</div>
          <div>
            <div class="timeline-title">{{ item.title }}</div>
            <p class="muted">{{ item.details }}</p>
          </div>
          <div class="pill success" v-if="item.status === 'done'">Livré</div>
          <div class="pill ghost" v-else>{{ item.status }}</div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchReport } from '../apiService'

const history = ref([])
const snapshot = ref({})
const loading = ref(true)
const error = ref(null)

const statCards = computed(() => [
  {
    label: 'Utilisateurs',
    value: snapshot.value.users ?? '—',
    subtitle: 'Comptes inscrits'
  },
  {
    label: 'Tirages',
    value: snapshot.value.draws ?? '—',
    subtitle: 'Tous jeux confondus'
  },
  {
    label: 'Favoris',
    value: snapshot.value.favoris ?? '—',
    subtitle: 'Grilles sauvegardées'
  },
  {
    label: 'Campagnes',
    value: snapshot.value.campagnes ?? '—',
    subtitle: 'Prêtes ou en cours'
  },
  {
    label: 'Sessions actives',
    value: snapshot.value.sessions ?? '—',
    subtitle: 'JWT présents en base'
  }
])

const loadReport = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await fetchReport()
    history.value = data.history || []
    snapshot.value = data.snapshot || {}
  } catch (e) {
    error.value = 'Impossible de charger le rapport'
  } finally {
    loading.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--muted);
}

.muted {
  color: var(--muted);
}

.snapshot {
  display: flex;
  gap: 0.5rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.card.error {
  border-color: #f87171;
  color: #fecdd3;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.stat h2 {
  margin: 0.1rem 0;
}

.timeline-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
}

.timeline-title {
  font-weight: 600;
}

.badge {
  padding: 0.35rem 0.6rem;
  border-radius: 12px;
  background: var(--accent-fade);
  color: var(--accent);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
}

.badge[data-area='auth'] { background: rgba(255, 168, 0, 0.15); color: #ffb547; }
.badge[data-area='games'] { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.badge[data-area='draws'] { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.badge[data-area='admin'] { background: rgba(248, 113, 113, 0.15); color: #f87171; }
.badge[data-area='ia'] { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }
.badge[data-area='infra'] { background: rgba(45, 212, 191, 0.15); color: #2dd4bf; }
.badge[data-area='bootstrap'] { background: rgba(248, 180, 0, 0.18); color: #f8b400; }

.pill {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.85rem;
}

.pill.success {
  background: rgba(74, 222, 128, 0.18);
  color: #22c55e;
}

.pill.ghost {
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
}

@media (max-width: 720px) {
  .timeline-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
