import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/style.css'

import Selection from './views/Selection.vue'
import Generateur from './views/Generateur.vue'
import Backtesting from './views/Backtesting.vue'
import Meteo from './views/Meteo.vue'
import Tendances from './views/Tendances.vue'
import Favoris from './views/Favoris.vue'
import Reducteur from './views/Reducteur.vue'
import Campagnes from './views/Campagnes.vue'
import GhostReport from './views/GhostReport.vue'
import TimelineAI from './views/TimelineAI.vue'
import Historique from './views/Historique.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Profile from './views/Profile.vue'
import Admin from './views/Admin.vue'
import Moderator from './views/Moderator.vue'
import Rapport from './views/Rapport.vue'
import { universes } from './universes'

const universeRoutes = universes.map((u) => ({
  path: u.basePath,
  component: u.entry
}))

const routes = [
  { path: '/', component: Selection },
  ...universeRoutes,
  { path: '/generateur', component: Generateur },
  { path: '/backtesting', component: Backtesting },
  { path: '/meteo', component: Meteo },
  { path: '/tendances', component: Tendances },
  { path: '/favoris', component: Favoris },
  { path: '/reducteur', component: Reducteur },
  { path: '/campagnes', component: Campagnes },
  { path: '/ghost', component: GhostReport },
  { path: '/timeline', component: TimelineAI },
  { path: '/historique', component: Historique },
  { path: '/rapport', component: Rapport },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/profile', component: Profile },
  { path: '/admin', component: Admin },
  { path: '/moderator', component: Moderator },
  { path: '/dashboard', redirect: '/euromillions' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')
