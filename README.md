# EuroMillions generator (offline-friendly)

## Installation
Les dépendances réseau étant limitées, le projet embarque des stubs minimalistes pour FastAPI et Pydantic. Aucune installation n’est requise pour exécuter les tests unitaires.

## Utilisation
1. Lancer les tests : `pytest`
2. Exemple de payload pour `/api/generate/frequency` :
   ```json
   {
     "draws": [
       {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]},
       {"numbers": [2, 3, 4, 5, 6], "stars": [2, 3]}
     ]
   }
   ```
3. Les réponses incluent `numbers`, `stars`, `confidence_score`, `method_used`, `explanation`, `features`.

## Routes disponibles hors-ligne
* `GET /` : page d'accueil listant EUROMILLION et EURODREAM, avec un rappel bilingue (fr/en) que le générateur est uniquement ludique, ne garantit aucun gain et invite à jouer de manière responsable.
* `POST /api/generate/{strategie}` : lance une stratégie (ex. `frequency`, `random`) avec un historique de tirages.
* `GET /api/health` : vérifie que le service répond.

## Validation des entrées
* Historique obligatoire (au moins un tirage)
* Respect des longueurs : 5 numéros, 2 étoiles
* Pas de doublons
* Bornes : numéros 1-50, étoiles 1-12

## Stratégies disponibles
* `frequency` : sélection des valeurs les plus fréquentes dans l’historique
* `random` : tirage aléatoire trié dans les bornes du profil de jeu
