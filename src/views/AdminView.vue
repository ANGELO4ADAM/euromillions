<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <header class="sticky top-0 z-20 backdrop-blur bg-slate-900/80 border-b border-slate-800">
      <div class="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between gap-4">
        <div>
          <p class="text-xs uppercase tracking-widest text-amber-300">Control Center</p>
          <h1 class="text-2xl font-semibold">EOP — Admin Console</h1>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="btn-secondary"
            @click="exportLogs"
            :disabled="loading.exportLogs"
          >
            <ArrowDownOnSquareStackIcon class="h-5 w-5" />
            Export Logs
          </button>
          <button
            class="btn-primary"
            @click="restartAll"
            :disabled="loading.restart"
          >
            <ArrowPathIcon class="h-5 w-5" />
            Restart Services
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-8 space-y-6">
      <section class="grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
        <AdminCard
          title="Database Control Center"
          description="Pilotage des données, optimisation et sauvegardes"
          icon="ServerIcon"
        >
          <div class="grid gap-4">
            <div class="grid grid-cols-2 gap-3 text-sm">
              <StatLine label="Total tirages" :value="stats.totalDraws" />
              <StatLine label="Total grilles" :value="stats.totalGrids" />
              <StatLine label="Taille base" :value="stats.dbSize" />
              <StatLine label="Dernier import" :value="stats.lastImport" />
              <StatLine label="Santé DB" :value="stats.dbHealth" />
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <button class="btn-neutral" @click="openDbExplorer">
                <MagnifyingGlassIcon class="h-5 w-5" />
                DB Explorer
              </button>
              <button class="btn-neutral" @click="runDbOptimizer" :disabled="loading.dbOptimize">
                <SparklesIcon class="h-5 w-5" />
                DB Optimizer
              </button>
              <button class="btn-neutral" @click="fixDuplicates" :disabled="loading.fixDuplicates">
                <AdjustmentsHorizontalIcon class="h-5 w-5" />
                Fix Duplicates
              </button>
              <button class="btn-neutral" @click="backupDb" :disabled="loading.backupDb">
                <ArrowDownTrayIcon class="h-5 w-5" />
                Backup DB (.zip)
              </button>
              <label class="btn-neutral cursor-pointer">
                <ArrowUpTrayIcon class="h-5 w-5" />
                Restore DB
                <input type="file" accept=".zip" class="hidden" @change="restoreDb" />
              </label>
            </div>
          </div>
        </AdminCard>

        <AdminCard
          title="IA Control Center"
          description="Pilotage des entraînements, modèles et comparaisons"
          icon="CpuChipIcon"
        >
          <div class="space-y-4">
            <div class="flex flex-wrap gap-2">
              <button class="btn-primary" @click="triggerTrain('standard')" :disabled="loading.train">
                <PlayCircleIcon class="h-5 w-5" />
                Entraînement Standard
              </button>
              <button class="btn-primary" @click="triggerTrain('intense')" :disabled="loading.trainIntense">
                <RocketLaunchIcon class="h-5 w-5" />
                Entraînement Intensif
              </button>
              <button class="btn-primary" @click="triggerTrain('targeted')" :disabled="loading.trainTargeted">
                <TargetIcon class="h-5 w-5" />
                Entraînement Ciblé
              </button>
            </div>
            <section class="space-y-2">
              <header class="flex items-center justify-between">
                <h3 class="text-sm font-semibold text-amber-200">Historique IA</h3>
                <button class="text-xs text-slate-300 hover:text-amber-200" @click="loadAiHistory">Rafraîchir</button>
              </header>
              <div class="overflow-hidden rounded-xl border border-slate-800/80">
                <table class="min-w-full text-xs md:text-sm">
                  <thead class="bg-slate-900/70 text-slate-300">
                    <tr>
                      <th class="px-3 py-2 text-left">Date</th>
                      <th class="px-3 py-2 text-left">Durée</th>
                      <th class="px-3 py-2 text-left">Modèle</th>
                      <th class="px-3 py-2 text-left">Score</th>
                      <th class="px-3 py-2 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="run in aiHistory" :key="run.id" class="border-t border-slate-800/60">
                      <td class="px-3 py-2">{{ run.date }}</td>
                      <td class="px-3 py-2">{{ run.duration }}</td>
                      <td class="px-3 py-2">{{ run.model }}</td>
                      <td class="px-3 py-2">{{ run.score }}</td>
                      <td class="px-3 py-2">
                        <button class="btn-ghost text-amber-200" @click="retrain(run.id)">
                          <ArrowPathRoundedSquareIcon class="h-4 w-4" />
                          Rejouer
                        </button>
                      </td>
                    </tr>
                    <tr v-if="aiHistory.length === 0">
                      <td colspan="5" class="px-3 py-4 text-center text-slate-400">Aucun historique disponible.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <IAComparator
              :models="aiModels"
              :metrics="comparatorMetrics"
              :selected="comparatorSelection"
              @update-selection="updateComparator"
            />

            <div class="flex flex-wrap gap-2">
              <button class="btn-neutral" @click="loadModels">Voir modèles IA disponibles</button>
              <button class="btn-neutral" @click="deleteModel" :disabled="!comparatorSelection.modelA">Supprimer modèle</button>
              <button class="btn-neutral" @click="restoreModel" :disabled="!deletedModel">Restaurer modèle précédent</button>
            </div>
          </div>
        </AdminCard>

        <AdminCard
          title="Tasks & Maintenance"
          description="Workers, tâches planifiées et redémarrages"
          icon="BoltIcon"
        >
          <div class="space-y-4">
            <section>
              <header class="flex items-center justify-between text-sm mb-2">
                <span class="text-amber-200 font-semibold">Monitoring Celery / Redis</span>
                <button class="text-xs text-slate-300 hover:text-amber-200" @click="loadCeleryStatus">Actualiser</button>
              </header>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <StatLine label="Workers" :value="celeryStatus.workers" />
                <StatLine label="Statut" :value="celeryStatus.status" />
                <StatLine label="Tâches en cours" :value="celeryStatus.tasks" />
                <StatLine label="Queue length" :value="celeryStatus.queueLength" />
                <StatLine label="Temps moyen" :value="celeryStatus.avgDuration" />
              </div>
            </section>

            <div class="flex flex-wrap gap-2 text-sm">
              <button class="btn-neutral" @click="restartService('backend')">Restart Backend</button>
              <button class="btn-neutral" @click="restartService('celery')">Restart Celery</button>
              <button class="btn-neutral" @click="restartService('scheduler')">Restart Scheduler</button>
            </div>

            <section class="space-y-3">
              <header class="text-amber-200 font-semibold text-sm">Planification automatique</header>
              <div class="space-y-2">
                <ToggleLine label="Entraîner IA chaque nuit" v-model="schedules.trainNightly" @change="persistSchedules" />
                <ToggleLine label="Import CSV chaque lundi" v-model="schedules.importCsvMonday" @change="persistSchedules" />
                <ToggleLine label="Lancer Back of the Future chaque dimanche" v-model="schedules.backFutureSunday" @change="persistSchedules" />
              </div>
            </section>
          </div>
        </AdminCard>

        <AdminCard
          title="System & Security Center"
          description="Logs, diagnostics et mode panic"
          icon="ShieldCheckIcon"
        >
          <div class="space-y-4">
            <LogsViewer
              :logs="systemLogs"
              :active-log="activeLog"
              @change-log="(val) => (activeLog = val)"
              @clear="clearLogs"
            />

            <section class="grid grid-cols-2 gap-3 text-sm">
              <StatLine label="Charge CPU" :value="systemHealth.cpu" />
              <StatLine label="RAM" :value="systemHealth.ram" />
              <StatLine label="Espace disque" :value="systemHealth.disk" />
              <StatLine label="Health Status" :value="systemHealth.status" />
            </section>

            <button class="btn-danger w-full" @click="panic" :disabled="loading.panic">
              <ExclamationTriangleIcon class="h-5 w-5" />
              Mode Panic : Stop all IA & tasks
            </button>
          </div>
        </AdminCard>
      </section>
    </main>

    <Modal v-if="ui.dbExplorer" title="DB Explorer" @close="ui.dbExplorer = false">
      <DBExplorer
        :tables="dbTables"
        :selected="selectedTable"
        :rows="tableRows"
        :loading="loading.table"
        :filter="tableFilter"
        @select="selectTable"
        @filter="(v) => (tableFilter = v)"
        @export="exportTableCsv"
      />
    </Modal>

    <ToastStack :items="toasts" @dismiss="dismissToast" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick, defineComponent } from 'vue'
import {
  ArrowDownOnSquareStackIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
  ArrowPathRoundedSquareIcon,
  ArrowUpTrayIcon,
  BoltIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  PlayCircleIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  SparklesIcon,
  TargetIcon,
  AdjustmentsHorizontalIcon,
  ArrowTrendingUpIcon,
  ServerIcon
} from '@heroicons/vue/24/outline'
import Chart from 'chart.js/auto'

const apiBase = ref('')
const loading = reactive({
  restart: false,
  exportLogs: false,
  dbOptimize: false,
  fixDuplicates: false,
  backupDb: false,
  table: false,
  train: false,
  trainIntense: false,
  trainTargeted: false,
  panic: false
})

const ui = reactive({ dbExplorer: false })
const stats = reactive({ totalDraws: 0, totalGrids: 0, dbSize: '—', lastImport: '—', dbHealth: '—' })
const dbTables = ref([])
const selectedTable = ref('')
const tableRows = ref([])
const tableFilter = ref('')
const aiHistory = ref([])
const aiModels = ref([])
const comparatorSelection = reactive({ modelA: '', modelB: '' })
const comparatorMetrics = reactive({
  rmse: { a: 0, b: 0 },
  accuracy: { a: 0, b: 0 },
  internal: { a: 0, b: 0 }
})
const deletedModel = ref('')
const celeryStatus = reactive({ workers: 0, status: '—', tasks: 0, queueLength: 0, avgDuration: '—' })
const schedules = reactive({ trainNightly: true, importCsvMonday: true, backFutureSunday: false })
const systemLogs = reactive({ backend: '', celery: '', ia: '' })
const activeLog = ref('backend')
const systemHealth = reactive({ cpu: '—', ram: '—', disk: '—', status: '—' })
const toasts = ref([])
let celeryInterval
let comparatorChart

const iconMap = {
  ServerIcon,
  CpuChipIcon,
  BoltIcon,
  ShieldCheckIcon
}

const apiFetch = async (path, options = {}) => {
  const response = await fetch(`${apiBase.value || ''}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  if (!response.ok) {
    const message = await safeText(response)
    throw new Error(message || `API error ${response.status}`)
  }
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return response.json()
  return response.blob ? response.blob() : response.text()
}

const safeText = async (res) => {
  try {
    return await res.text()
  } catch (e) {
    return ''
  }
}

const pushToast = (title, type = 'success') => {
  const id = crypto.randomUUID()
  toasts.value.push({ id, title, type })
  setTimeout(() => dismissToast(id), 4000)
}

const dismissToast = (id) => {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

const loadStats = async () => {
  try {
    const data = await apiFetch('/api/admin/stats')
    Object.assign(stats, data || {})
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const openDbExplorer = async () => {
  ui.dbExplorer = true
  try {
    dbTables.value = await apiFetch('/api/admin/db/tables')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const selectTable = async (table) => {
  selectedTable.value = table
  if (!table) return
  loading.table = true
  try {
    const data = await apiFetch(`/api/admin/db/table/${table}`)
    tableRows.value = Array.isArray(data?.rows) ? data.rows : data
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.table = false
  }
}

const exportTableCsv = () => {
  const rows = tableRows.value
  if (!rows?.length) return pushToast('Aucune donnée à exporter', 'error')
  const headers = Object.keys(rows[0])
  const csv = [headers.join(',')]
    .concat(rows.map((row) => headers.map((h) => JSON.stringify(row[h] ?? '')).join(',')))
    .join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedTable.value || 'table'}.csv`
  a.click()
  URL.revokeObjectURL(url)
  pushToast('Export CSV prêt')
}

const runDbOptimizer = async () => {
  loading.dbOptimize = true
  try {
    await apiFetch('/api/admin/db/vacuum', { method: 'POST' })
    pushToast('Vacuum lancé')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.dbOptimize = false
  }
}

const fixDuplicates = async () => {
  loading.fixDuplicates = true
  try {
    await apiFetch('/api/admin/db/fix-duplicates', { method: 'POST' })
    pushToast('Déduplication lancée')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.fixDuplicates = false
  }
}

const backupDb = async () => {
  loading.backupDb = true
  try {
    const blob = await apiFetch('/api/admin/db/backup', { method: 'POST' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'eop-backup.zip'
    a.click()
    URL.revokeObjectURL(url)
    pushToast('Backup téléchargé')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.backupDb = false
  }
}

const restoreDb = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    await fetch(`${apiBase.value}/api/admin/db/restore`, { method: 'POST', body: formData })
    pushToast('Restauration lancée')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const triggerTrain = async (mode) => {
  const map = {
    standard: { path: '/api/admin/train', flag: 'train' },
    intense: { path: '/api/admin/train-intense', flag: 'trainIntense' },
    targeted: { path: '/api/admin/train-targeted', flag: 'trainTargeted' }
  }
  const entry = map[mode]
  if (!entry) return
  loading[entry.flag] = true
  try {
    await apiFetch(entry.path, { method: 'POST' })
    pushToast(`Entraînement ${mode} lancé`)
    loadAiHistory()
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading[entry.flag] = false
  }
}

const loadAiHistory = async () => {
  try {
    const data = await apiFetch('/api/admin/ai/history')
    aiHistory.value = data || []
    hydrateComparatorFromHistory()
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const hydrateComparatorFromHistory = () => {
  if (!aiHistory.value.length) return
  const first = aiHistory.value[0]
  comparatorSelection.modelA = comparatorSelection.modelA || first.model
  comparatorSelection.modelB = comparatorSelection.modelB || aiHistory.value[1]?.model || first.model
  const metrics = aiHistory.value.reduce(
    (acc, run) => {
      acc[run.model] = {
        rmse: run.rmse ?? run.score ?? 0,
        accuracy: run.accuracy ?? 0,
        internal: run.internal ?? run.score ?? 0
      }
      return acc
    },
    {}
  )
  comparatorMetrics.rmse.a = metrics[comparatorSelection.modelA]?.rmse ?? 0
  comparatorMetrics.rmse.b = metrics[comparatorSelection.modelB]?.rmse ?? 0
  comparatorMetrics.accuracy.a = metrics[comparatorSelection.modelA]?.accuracy ?? 0
  comparatorMetrics.accuracy.b = metrics[comparatorSelection.modelB]?.accuracy ?? 0
  comparatorMetrics.internal.a = metrics[comparatorSelection.modelA]?.internal ?? 0
  comparatorMetrics.internal.b = metrics[comparatorSelection.modelB]?.internal ?? 0
}

const updateComparator = ({ modelA, modelB }) => {
  comparatorSelection.modelA = modelA
  comparatorSelection.modelB = modelB
  hydrateComparatorFromHistory()
  nextTick(drawComparatorChart)
}

const drawComparatorChart = async () => {
  await nextTick()
  const ctx = document.getElementById('ia-compare')
  if (!ctx) return
  const data = {
    labels: ['RMSE', 'Précision %', 'Score interne'],
    datasets: [
      {
        label: comparatorSelection.modelA || 'Model A',
        backgroundColor: 'rgba(251, 191, 36, 0.2)',
        borderColor: 'rgba(251, 191, 36, 0.9)',
        borderWidth: 2,
        data: [comparatorMetrics.rmse.a, comparatorMetrics.accuracy.a, comparatorMetrics.internal.a]
      },
      {
        label: comparatorSelection.modelB || 'Model B',
        backgroundColor: 'rgba(56, 189, 248, 0.2)',
        borderColor: 'rgba(56, 189, 248, 0.9)',
        borderWidth: 2,
        data: [comparatorMetrics.rmse.b, comparatorMetrics.accuracy.b, comparatorMetrics.internal.b]
      }
    ]
  }
  if (comparatorChart) comparatorChart.destroy()
  comparatorChart = new Chart(ctx, {
    type: 'radar',
    data,
    options: {
      scales: { r: { beginAtZero: true, angleLines: { color: '#1e293b' }, grid: { color: '#1e293b' } } },
      plugins: { legend: { labels: { color: '#e2e8f0' } } }
    }
  })
}

const loadModels = async () => {
  try {
    const data = await apiFetch('/api/admin/ai/models')
    aiModels.value = data || []
    if (!comparatorSelection.modelA && aiModels.value[0]) comparatorSelection.modelA = aiModels.value[0]
    if (!comparatorSelection.modelB && aiModels.value[1]) comparatorSelection.modelB = aiModels.value[1]
    drawComparatorChart()
    pushToast('Modèles IA chargés')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const retrain = async (id) => {
  try {
    await apiFetch('/api/admin/ai/retrain', { method: 'POST', body: JSON.stringify({ id }) })
    pushToast('Relance entraînement')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const deleteModel = async () => {
  if (!comparatorSelection.modelA) return
  try {
    await apiFetch('/api/admin/ai/model/delete', {
      method: 'POST',
      body: JSON.stringify({ model: comparatorSelection.modelA })
    })
    deletedModel.value = comparatorSelection.modelA
    pushToast('Modèle supprimé')
    loadModels()
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const restoreModel = async () => {
  if (!deletedModel.value) return
  try {
    await apiFetch('/api/admin/ai/model/restore', {
      method: 'POST',
      body: JSON.stringify({ model: deletedModel.value })
    })
    pushToast('Modèle restauré')
    deletedModel.value = ''
    loadModels()
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const loadCeleryStatus = async () => {
  try {
    const data = await apiFetch('/api/admin/celery-status')
    Object.assign(celeryStatus, data || {})
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const restartService = async (service) => {
  const map = {
    backend: '/api/admin/restart/backend',
    celery: '/api/admin/restart/celery',
    scheduler: '/api/admin/restart/scheduler'
  }
  const path = map[service]
  if (!path) return
  try {
    await apiFetch(path, { method: 'POST' })
    pushToast(`${service} redémarré`)
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const persistSchedules = async () => {
  try {
    await apiFetch('/api/admin/restart/scheduler', {
      method: 'POST',
      body: JSON.stringify({ schedules })
    })
    pushToast('Planification mise à jour')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const exportLogs = async () => {
  loading.exportLogs = true
  try {
    const blob = await apiFetch('/api/admin/logs')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'eop-logs.txt'
    a.click()
    URL.revokeObjectURL(url)
    pushToast('Logs exportés')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.exportLogs = false
  }
}

const clearLogs = async () => {
  try {
    await apiFetch('/api/admin/logs/clear', { method: 'POST' })
    systemLogs.backend = ''
    systemLogs.celery = ''
    systemLogs.ia = ''
    pushToast('Logs nettoyés')
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const loadLogs = async () => {
  try {
    const data = await apiFetch('/api/admin/logs')
    systemLogs.backend = data?.backend || ''
    systemLogs.celery = data?.celery || ''
    systemLogs.ia = data?.ia || ''
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const loadSystemHealth = async () => {
  try {
    const data = await apiFetch('/api/admin/system-health')
    Object.assign(systemHealth, data || {})
  } catch (err) {
    pushToast(err.message, 'error')
  }
}

const panic = async () => {
  loading.panic = true
  try {
    await apiFetch('/api/admin/panic', { method: 'POST' })
    pushToast('Mode panic activé')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.panic = false
  }
}

const restartAll = async () => {
  loading.restart = true
  try {
    await Promise.all([
      apiFetch('/api/admin/restart/backend', { method: 'POST' }),
      apiFetch('/api/admin/restart/celery', { method: 'POST' }),
      apiFetch('/api/admin/restart/scheduler', { method: 'POST' })
    ])
    pushToast('Services relancés')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    loading.restart = false
  }
}

const handleSystemRefresh = () => {
  loadCeleryStatus()
  loadSystemHealth()
}

const setupIntervals = () => {
  celeryInterval = setInterval(handleSystemRefresh, 20000)
}

onMounted(() => {
  loadStats()
  openDbExplorer()
  loadAiHistory().then(drawComparatorChart)
  loadModels()
  loadCeleryStatus()
  loadLogs()
  loadSystemHealth()
  setupIntervals()
})

onBeforeUnmount(() => {
  if (celeryInterval) clearInterval(celeryInterval)
  if (comparatorChart) comparatorChart.destroy()
})

watch(
  () => ({ ...comparatorMetrics, ...comparatorSelection }),
  () => drawComparatorChart(),
  { deep: true }
)

const AdminCard = defineComponent({
  name: 'AdminCard',
  props: {
    title: String,
    description: String,
    icon: String
  },
  setup(props, { slots }) {
    const iconComponent = computed(() => iconMap[props.icon] || ServerIcon)
    return { iconComponent, slots }
  },
  template: `
    <div class="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl shadow-black/30">
      <div class="absolute inset-0 bg-gradient-to-br from-amber-500/10 via-slate-800/30 to-cyan-400/10 opacity-0 transition-opacity duration-500 group-hover:opacity-100"></div>
      <div class="relative flex items-center gap-3 mb-3">
        <div class="rounded-xl bg-slate-800/70 p-2 border border-slate-700">
          <component :is="iconComponent" class="h-6 w-6 text-amber-300" />
        </div>
        <div>
          <h2 class="text-lg font-semibold">{{ title }}</h2>
          <p class="text-sm text-slate-300">{{ description }}</p>
        </div>
      </div>
      <div class="relative">
        <slot />
      </div>
    </div>
  `
})

const StatLine = defineComponent({
  name: 'StatLine',
  props: { label: String, value: [String, Number] },
  template: `
    <div class="flex items-center justify-between rounded-lg bg-slate-900/70 border border-slate-800 px-3 py-2">
      <span class="text-slate-300">{{ label }}</span>
      <span class="font-semibold text-amber-200">{{ value ?? '—' }}</span>
    </div>
  `
})

const ToggleLine = defineComponent({
  name: 'ToggleLine',
  props: { label: String, modelValue: Boolean },
  emits: ['update:modelValue', 'change'],
  methods: {
    toggle() {
      this.$emit('update:modelValue', !this.modelValue)
      this.$emit('change', !this.modelValue)
    }
  },
  template: `
    <label class="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/70 px-3 py-2 cursor-pointer">
      <span class="text-slate-200">{{ label }}</span>
      <button
        class="relative inline-flex h-6 w-11 items-center rounded-full transition"
        :class="modelValue ? 'bg-amber-400' : 'bg-slate-600'"
        type="button"
        @click="toggle"
      >
        <span class="inline-block h-5 w-5 transform rounded-full bg-white transition" :class="modelValue ? 'translate-x-5' : 'translate-x-1'"></span>
      </button>
    </label>
  `
})

const Modal = defineComponent({
  name: 'Modal',
  props: { title: String },
  emits: ['close'],
  methods: { close() { this.$emit('close') } },
  template: `
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur">
      <div class="w-full max-w-5xl rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
        <header class="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div>
            <p class="text-xs uppercase tracking-widest text-amber-300">Admin Modal</p>
            <h3 class="text-lg font-semibold">{{ title }}</h3>
          </div>
          <button class="text-slate-300 hover:text-amber-200" @click="close">✕</button>
        </header>
        <div class="p-4 max-h-[70vh] overflow-y-auto"><slot /></div>
      </div>
    </div>
  `
})

const LogsViewer = defineComponent({
  name: 'LogsViewer',
  props: {
    logs: Object,
    activeLog: String
  },
  emits: ['change-log', 'clear'],
  data() {
    return {
      tabs: [
        { key: 'backend', label: 'Logs backend' },
        { key: 'celery', label: 'Logs Celery' },
        { key: 'ia', label: 'Logs IA' }
      ]
    }
  },
  template: `
    <div class="rounded-xl border border-slate-800 bg-slate-900/70">
      <header class="flex items-center justify-between px-3 py-2 border-b border-slate-800">
        <div class="flex gap-2">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="text-xs px-3 py-1 rounded-lg"
            :class="activeLog === tab.key ? 'bg-amber-400/20 text-amber-200' : 'text-slate-300 hover:text-amber-200'"
            @click="$emit('change-log', tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>
        <button class="text-xs text-rose-300 hover:text-rose-200" @click="$emit('clear')">Clear Logs</button>
      </header>
      <pre class="max-h-48 overflow-y-auto p-3 text-xs text-slate-200 bg-slate-950/60">{{ logs?.[activeLog] || 'Aucun log' }}</pre>
    </div>
  `
})

const IAComparator = defineComponent({
  name: 'IAComparator',
  props: {
    models: Array,
    metrics: Object,
    selected: Object
  },
  emits: ['update-selection'],
  methods: {
    update(key, value) {
      this.$emit('update-selection', { ...this.selected, [key]: value })
    }
  },
  components: { ArrowTrendingUpIcon },
  template: `
    <div class="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs uppercase tracking-widest text-amber-300">Comparateur IA</p>
          <h4 class="text-sm font-semibold">Comparer deux modèles</h4>
        </div>
        <ArrowTrendingUpIcon class="h-5 w-5 text-amber-200" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1">
          <label class="text-xs text-slate-400">Model A</label>
          <select class="input" :value="selected?.modelA" @change="(e) => update('modelA', e.target.value)">
            <option value="">Choisir</option>
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs text-slate-400">Model B</label>
          <select class="input" :value="selected?.modelB" @change="(e) => update('modelB', e.target.value)">
            <option value="">Choisir</option>
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>
      <canvas id="ia-compare" class="w-full h-52"></canvas>
    </div>
  `
})

const DBExplorer = defineComponent({
  name: 'DBExplorer',
  props: {
    tables: Array,
    selected: String,
    rows: Array,
    loading: Boolean,
    filter: String
  },
  emits: ['select', 'filter', 'export'],
  components: { ArrowPathIcon },
  computed: {
    filteredRows() {
      if (!this.filter) return this.rows
      const f = this.filter.toLowerCase()
      return this.rows?.filter((row) => Object.values(row).some((v) => String(v).toLowerCase().includes(f)))
    }
  },
  template: `
    <div class="grid md:grid-cols-3 gap-4">
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-semibold text-amber-200">Tables</h4>
          <button class="btn-ghost text-xs" @click="$emit('export')">Export CSV</button>
        </div>
        <div class="rounded-xl border border-slate-800 bg-slate-900/70 max-h-80 overflow-y-auto">
          <button
            v-for="table in tables"
            :key="table"
            class="w-full text-left px-3 py-2 border-b border-slate-800/60 hover:bg-slate-800/60"
            :class="selected === table ? 'bg-amber-400/10 text-amber-200' : 'text-slate-200'"
            @click="$emit('select', table)"
          >
            {{ table }}
          </button>
        </div>
      </div>
      <div class="md:col-span-2 space-y-3">
        <div class="flex items-center gap-3">
          <input
            class="input flex-1"
            placeholder="Filtrer les lignes"
            :value="filter"
            @input="$emit('filter', $event.target.value)"
          />
          <button class="btn-neutral" @click="$emit('select', selected)">
            <ArrowPathIcon class="h-5 w-5" />
          </button>
        </div>
        <div class="rounded-xl border border-slate-800 bg-slate-950/60 max-h-96 overflow-auto">
          <p v-if="loading" class="p-3 text-sm text-slate-300">Chargement...</p>
          <table v-else-if="filteredRows && filteredRows.length" class="min-w-full text-xs md:text-sm">
            <thead class="bg-slate-900/70 text-amber-200">
              <tr>
                <th v-for="col in Object.keys(filteredRows[0] || {})" :key="col" class="px-3 py-2 text-left">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in filteredRows" :key="idx" :class="['border-t border-slate-800/60', idx % 2 === 0 ? 'bg-slate-900/40' : '']">
                <td v-for="(v, key) in row" :key="key" class="px-3 py-2 whitespace-nowrap">{{ v }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="p-3 text-sm text-slate-400">Aucune donnée pour cette table.</p>
        </div>
      </div>
    </div>
  `
})

const ToastStack = defineComponent({
  name: 'ToastStack',
  props: { items: Array },
  emits: ['dismiss'],
  template: `
    <div class="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
      <div
        v-for="toast in items"
        :key="toast.id"
        class="shadow-lg rounded-lg px-4 py-3 border text-sm"
        :class="toast.type === 'error' ? 'bg-rose-500/90 border-rose-300 text-white' : 'bg-emerald-500/90 border-emerald-200 text-white'"
      >
        <div class="flex items-center justify-between gap-3">
          <span>{{ toast.title }}</span>
          <button class="text-white/80" @click="$emit('dismiss', toast.id)">✕</button>
        </div>
      </div>
    </div>
  `
})
</script>

<style scoped>
.btn-primary {
  @apply inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-amber-500/30 transition hover:from-amber-400 hover:to-amber-500 disabled:opacity-60;
}
.btn-secondary {
  @apply inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2 text-sm font-semibold text-slate-100 border border-slate-700 hover:border-amber-300/60 transition disabled:opacity-60;
}
.btn-neutral {
  @apply inline-flex items-center justify-center gap-2 rounded-lg bg-slate-800/80 px-3 py-2 text-sm font-semibold text-slate-100 border border-slate-700 hover:border-amber-300/60 transition w-full;
}
.btn-ghost {
  @apply inline-flex items-center gap-1 rounded-lg px-2 py-1 hover:text-amber-200;
}
.btn-danger {
  @apply inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-rose-500 to-rose-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-rose-500/30 transition hover:from-rose-400 hover:to-rose-500 disabled:opacity-60;
}
.input {
  @apply w-full rounded-lg border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 focus:border-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-200/50;
}
</style>
