# Euro-Optimiseur Pro (EOP)

Euro-Optimiseur Pro fournit une base complète pour l'écosystème EuroMillions :
- API Flask sur le port 8080 avec routes d'authentification, tirages, campagnes, admin et génération de grilles.
- Workers Celery reliés à Redis pour les tâches asynchrones (import, entraînement, sonar, maintenance).
- Frontend Vue 3 + Vite (port 5173) avec pages Dashboard, Générateur, Backtesting, Admin et plus.
- Base SQLite `euromillions.db` initialisée automatiquement avec persistance des sessions JWT sécurisés.
- Page d'entrée pour choisir l'univers EuroMillions ou EuroDream (navigation adaptée dès le choix effectué).

## Démarrage rapide
```
JWT_SECRET="change-me" JWT_TTL_SECONDS=86400 python app_factory.py
npm install
npm run dev
```

Navigation :
- Page d'accueil `/` = sélecteur d'univers (EuroMillions / EuroDream)
- Espace EuroMillions : `/euromillions` (plus les pages fonctionnelles habituelles)
- Espace EuroDream dédié : `/eurodream` (miroir des stratégies et analytics, isolé via paramètre `game=eurodream`)
- Frontend organisé par univers : `src/universes/euromillions` et `src/universes/eurodream` pour éviter les confusions.
- Backend : répertoires `games/euromillions` et `games/eurodream` décrivent les profils (plages, cardinalités) et sont agrégés via `games/registry.py`.
- Parité fonctionnelle : EuroDream transporte les mêmes capacités que l'univers EuroMillions (référence Romignon) et le registre `/api/games/registry` expose un indicateur de parité pour rassurer la navigation et les validations.

Authentification :
- `/api/auth/login` émet un JWT signé (HS256) contenant `sub`, `role`, `iat` et `exp`.
- Le token est stocké dans la table `sessions` avec date d'expiration et peut être révoqué via `/api/auth/logout`.
- Envoyer toujours `Authorization: Bearer <token>` sur les routes protégées; les rôles `admin`/`moderator` sont appliqués côté serveur.

Analytique : l'API propose `/api/draws/analytics` pour calculer les fréquences des numéros/étoiles déjà enregistrés, avec un paramètre `game` pour isoler EuroMillions ou EuroDream.

Génération : toutes les routes `/api/generate/<strategie>` acceptent `game` (`euromillions` ou `eurodream`). Une stratégie Monte-Carlo + Fibonacci dédiée est exposée via `/api/generate/monte_carlo_fibo` (200 itérations pondérées) et disponible côté EuroDream. Le frontend propose un menu Générateur multi-stratégies (8+ cartes : Meta IA, Fibonacci inversé, MCC, XGBoost, 3GS, Spectre, Timeline AI, Echo des Écarts, Monte-Carlo Fibo) pour déclencher rapidement la stratégie souhaitée.

Registry : `/api/games/registry` expose les profils de jeux (plages, cardinalités) ainsi que la liste des stratégies autorisées pour sécuriser le frontend et synchroniser les validations.

Surveillance : `/api/health` fournit un signal de vie minimal (connectivité DB, comptages clés, jeux disponibles, stratégies activées) pour les checks automatisés ou l’observabilité légère.

Audit des stratégies : `/api/strategies/report` (authentifié) fournit un classement des stratégies embarquées, vérifie la présence des modules d'implémentation et renvoie un score/état par stratégie et par univers demandé (`?game=euromillions|eurodream`).

Bootstrap rapide : `/api/admin/bootstrap_data` (admin) injecte des tirages de démonstration par univers (minimum paramétrable) afin que les écrans EuroMillions/EuroDream disposent toujours de données de navigation et d'analytics.

Validation renforcée : les tirages et favoris exigent désormais des numéros/étoiles uniques, triés et conformes à chaque profil de jeu pour éviter les incohérences.

Robustesse : des index SQLite couvrent `draws (game, draw_date)`, `favorites (user_id, game)` et `campagnes (game)` pour stabiliser les consultations multi-univers et limiter les scans complets.

Supervision : `/api/admin/rapport` fournit un instantané opérationnel (volumétrie utilisateurs/tirages/favoris/campagnes, sessions actives, derniers tirages et éventuels trous de calendrier) pour aider l'admin à suivre la santé de la plateforme.

Rapport consolidé : `/api/report/history` agrège la chronologie des fonctionnalités livrées (A → Z) ainsi qu'un snapshot des métriques clés (utilisateurs, tirages, favoris, campagnes, sessions) exposé côté frontend via la page "Rapport".

Les scripts `start_all.sh` et `stop_all.sh` aident à lancer ou arrêter l'ensemble des services.
