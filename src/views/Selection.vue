<template>
  <section class="landing floating-lights">
    <div class="landing-card panel-aurora">
      <h1 class="title glow-title">Choisissez votre univers</h1>
      <p class="subtitle">Accédez à l'expérience complète EuroMillions ou explorez la nouvelle EuroDream.</p>
      <div class="choices">
        <button
          v-for="game in gamesToShow"
          :key="game.key"
          class="choice"
          :class="{ alt: game.key === 'eurodream' }"
          @click="goTo(game.key)"
        >
          <span v-if="game.key === 'euromillions'" class="badge">Recommandé</span>
          <strong>{{ game.label }}</strong>
          <small>
            {{ game.numbers_count }} numéros / {{ game.stars_count }} étoiles • {{ strategiesText }} stratégies IA
          </small>
          <small class="meta">Plage: 1-{{ game.numbers }} / 1-{{ game.stars }}</small>
          <small class="parity" v-if="game.parity_label">{{ game.parity_label }}</small>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchGamesRegistry } from '../apiService'

const router = useRouter()
const games = ref([])
const strategies = ref([])

const fallbackGames = [
  {
    key: 'euromillions',
    label: 'EuroMillions',
    numbers: 50,
    numbers_count: 5,
    stars: 12,
    stars_count: 2,
    parity_label: "Univers de référence pour la parité fonctionnelle"
  },
  {
    key: 'eurodream',
    label: 'EuroDream',
    numbers: 50,
    numbers_count: 5,
    stars: 12,
    stars_count: 2,
    parity_with: 'euromillions',
    parity_label: "Parité fonctionnelle avec l'univers EuroMillions (ref. Romignon)"
  }
]

const gamesToShow = computed(() => (games.value.length ? games.value : fallbackGames))
const strategiesText = computed(() => (strategies.value.length ? strategies.value.length : 'multi'))

onMounted(async () => {
  try {
    const { data } = await fetchGamesRegistry()
    games.value = data.games || []
    strategies.value = data.strategies || []
  } catch (error) {
    console.warn('Impossible de récupérer le registre des jeux', error)
  }
})

const goTo = (key) => router.push(`/${key}`)
</script>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: radial-gradient(circle at 20% 20%, rgba(168, 85, 247, 0.25), transparent 40%),
    radial-gradient(circle at 80% 0%, rgba(236, 72, 153, 0.24), transparent 30%),
    var(--bg-gradient, var(--bg-primary));
}

.landing-card {
  position: relative;
  padding: 2.5rem;
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.3);
  max-width: 820px;
  width: 100%;
  overflow: hidden;
}

.title {
  margin: 0 0 0.5rem;
  font-size: 2rem;
}

.subtitle {
  margin: 0 0 1.5rem;
  color: var(--text-muted);
}

.choices {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.choice {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(236,72,153,0.08));
  color: var(--text-primary);
  text-align: left;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.choice:hover {
  transform: translateY(-2px);
  border-color: var(--accent);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(168, 85, 247, 0.4);
}

.choice strong {
  font-size: 1.1rem;
}

.choice small {
  color: var(--text-muted);
}

.choice .meta {
  display: block;
  font-size: 0.85rem;
}

.choice.alt {
  background: linear-gradient(135deg, rgba(56,189,248,0.12), rgba(14,165,233,0.08));
}

.badge {
  align-self: flex-start;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #fff;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.parity {
  display: block;
  color: var(--text-muted);
  font-size: 0.85rem;
}
</style>
