# EuroMillions generator (offline-friendly)

## Installation
Les dépendances réseau étant limitées, le projet embarque des stubs minimalistes pour FastAPI et Pydantic. Aucune installation n’est requise pour exécuter les tests unitaires.

## Utilisation
1. Lancer les tests : `pytest` (ou `make test`)
2. Installer les dépendances réelles : `pip install -r requirements.txt` (ou `make install`)
3. Démarrer l'API réelle (avec CORS ouvert pour la preview) :
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   ou simplement `make serve`.
4. Prévisualiser l'interface et piloter l'API :
   * Ouvrir `frontend/index.html` (fichier local ou via `python -m http.server --directory frontend 8001` ou `make frontend`)
   * Sélectionner le jeu (`EUROMILLION` ou `EURODREAM`), la stratégie, garder ou modifier le payload d'exemple, puis cliquer sur **Call API**.
   * Par défaut, le frontend appelle `http://localhost:8000` si l'origine est `file://` ; sinon il utilise l'origine actuelle. Un champ "API base" permet de cibler un autre backend.
4. Exemple de payload pour `/api/generate/frequency` (le champ `game` peut valoir `euromillion` ou `eurodream`) :
   ```json
   {
     "draws": [
       {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]},
       {"numbers": [2, 3, 4, 5, 6], "stars": [2, 3]}
     ],
     "game": "eurodream",
     "use_manual_draws": false
   }
   ```
4. Les réponses incluent `numbers`, `stars`, `confidence_score`, `method_used`, `explanation`, `features`.
5. Si le scraping échoue, un administrateur peut ajouter des tirages manuellement via `POST /api/admin/manual-draws` (voir ci-dessous)
   puis les consulter via `GET /api/admin/manual-draws/{game}` ou les purger via `DELETE /api/admin/manual-draws/{game}`. Chaque tirage peut
   embarquer un champ optionnel `draw_date` (YYYY-MM-DD) pour permettre des filtres par jour de la semaine. Le chemin du fichier stocké peut
   être ajusté avec `MANUAL_DRAWS_PATH`. Un résumé global des tirages manuels par jeu est disponible via `GET /api/admin/manual-draws` et
   un export complet du store pour backup via `GET /api/admin/manual-draws/backup`.
6. Le champ `use_manual_draws` (bool) permet, côté génération, d'inclure automatiquement l'historique persistant importé par l'administrateur
   pour le jeu ciblé. Si aucune donnée n'est disponible et que `draws` est vide, l'appel renverra un 404 explicite. L'ingestion manuelle accepte
   aussi un flag `replace` pour remplacer intégralement l'historique d'un jeu.
7. Publication GitHub Pages :
   * Exécuter `make pages` pour copier le frontend statique dans `docs/` (le dossier par défaut supporté par GitHub Pages).
   * Pousser la branche et activer GitHub Pages sur la racine `docs/` depuis les paramètres du dépôt.
   * L’URL publiée servira automatiquement le `index.html` existant avec les assets inclus (CSS/JS inline), sans dépendances externes.

## Routes disponibles hors-ligne
* `GET /` : page d'accueil listant EUROMILLION et EURODREAM, avec un rappel bilingue (fr/en) que le générateur est uniquement ludique, ne garantit aucun gain et invite à jouer de manière responsable.
* `POST /api/generate/{strategie}` : lance une stratégie (ex. `frequency`, `random`, `fibo`, `mcc`, `spectre`, `meta_ia`) avec un historique de tirages.
* `POST /api/admin/manual-draws` : ingestion manuelle d'un ou plusieurs tirages validés (fallback en cas d'échec du scraping), avec support d'un champ `draw_date` (YYYY-MM-DD) et d'un booléen `replace` pour écraser l'existant.
* `GET /api/admin/manual-draws` : résumé par jeu (compte et dernière date de tirage persistée) pour le fallback manuel.
* `GET /api/admin/manual-draws/backup` : export complet du store persistant (JSON) pour backup/archivage rapide.
* `GET /api/admin/manual-draws/{game}` : retourne les tirages manuellement saisis pour le jeu ciblé, avec un filtre optionnel `weekday` (1-7 ou nom du jour en fr/en).
* `DELETE /api/admin/manual-draws/{game}` : supprime tout l'historique manuel pour le jeu ciblé.
* `POST /api/admin/train` / `GET /api/admin/train` : stub de déclenchement et de suivi de training (manual ou auto), utile pour tracer les runs et les backups d'entrée.
* Console admin (stubs complets pour le dashboard Vue) :
  * `GET /api/admin/stats` : métriques synthétiques (tirages, taille du store, dernier import, santé DB)
  * `GET /api/admin/db/tables` / `GET /api/admin/db/table/{name}` : exploration des tables virtuelles (`manual_draws`, `training_runs`, `ai_models`)
  * `POST /api/admin/db/vacuum` / `POST /api/admin/db/fix-duplicates` : actions de maintenance simulées (loguées)
  * `POST /api/admin/db/backup` / `POST /api/admin/db/restore` : snapshot/restauration du store et des états admin
  * `POST /api/admin/train-intense` / `POST /api/admin/train-targeted` : modes d'entraînement supplémentaires, alimentant l'historique IA
  * `GET /api/admin/ai/history` / `POST /api/admin/ai/retrain` : historique des runs IA et relance ciblée
  * `GET /api/admin/ai/models` / `POST /api/admin/ai/model/delete` / `POST /api/admin/ai/model/restore` : gestion des modèles disponibles
  * `GET /api/admin/celery-status` / `POST /api/admin/restart/{backend|celery|scheduler}` : monitoring et redémarrage de services
  * `GET /api/admin/logs` / `POST /api/admin/logs/clear` : consultation/vidage des logs (backend, Celery, IA)
  * `GET /api/admin/system-health` / `POST /api/admin/panic` : diagnostics système et mode panic (safe mode)
* `GET /api/health` : vérifie que le service répond et expose les jeux/stratégies disponibles.

## Prototype UI (offline)
* Ouvrir `frontend/index.html` directement dans un navigateur pour prévisualiser une landing moderne (dégradés subtils, cartes vitrée, typographie Inter/Space Grotesk).
* Les sections clés : héros avec CTA, cartes jeux (EUROMILLION/EURODREAM), sélecteur de stratégies, admin/fallback manuel (import, filtre par jour, résumé, purge),
  générateur live, insights et rappel bilingue de jeu responsable.

## Validation des entrées
* Historique obligatoire (au moins un tirage)
* Respect des longueurs : 5 numéros, 2 étoiles
* Pas de doublons
* Bornes : numéros 1-50, étoiles 1-12

## Stratégies disponibles
* `frequency` : sélection des valeurs les plus fréquentes dans l’historique
* `random` : tirage aléatoire trié dans les bornes du profil de jeu
* `fibo` : exploite les intervalles Fibonacci (1,2,3,5,8,13) pour extraire les valeurs récurrentes
* `mcc` : pondération inversée sur les 80 derniers tirages pour favoriser les numéros/étoiles en retard
* `spectre` : compare court terme (20) et long terme (120) pour détecter des retours probables
* `meta_ia` : consensus entre FIBO, MCC et SPECTRE pour stabiliser la grille
