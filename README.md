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
     "game": "eurodream"
   }
   ```
4. Les réponses incluent `numbers`, `stars`, `confidence_score`, `method_used`, `explanation`, `features`.

## Routes disponibles hors-ligne
* `GET /` : page d'accueil listant EUROMILLION et EURODREAM, avec un rappel bilingue (fr/en) que le générateur est uniquement ludique, ne garantit aucun gain et invite à jouer de manière responsable.
* `POST /api/generate/{strategie}` : lance une stratégie (ex. `frequency`, `random`, `fibo`, `mcc`, `spectre`, `meta_ia`) avec un historique de tirages.
* `GET /api/health` : vérifie que le service répond et expose les jeux/stratégies disponibles.

## Prototype UI (offline)
* Ouvrir `frontend/index.html` directement dans un navigateur pour prévisualiser une landing moderne (dégradés subtils, cartes vitrée, typographie Inter/Space Grotesk).
* Les sections clés : héros avec CTA, cartes jeux (EUROMILLION/EURODREAM), sélecteur de stratégies, insights et rappel bilingue de jeu responsable.

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
