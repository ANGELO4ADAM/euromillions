# Propositions de design pour l'interface Euromillions

## État du style actuel (capture fournie)
- Dominante violet/fuchsia avec dégradés et cartes arrondies.
- Cartes empilées avec boutons colorés; mise en avant des stratégies IA et des statistiques.
- Points à améliorer : contraste parfois faible sur fond très saturé, hiérarchie visuelle peu structurée (beaucoup de couleurs d'appel), lisibilité des blocs de texte (interlignage faible), manque de repères pour séparer navigation, contenu et actions primaires.

## Direction 1 : Neo-Gradient modernisé (raffinement du style fourni)
- **Palette** : base violet nuit (#20124d) avec dégradé secondaire magenta→turquoise en accent; textes gris clair (#e8e8f0) et titres blancs.
- **Typo** : titres en "Inter SemiBold", corps en "Inter Regular" (line-height 1.6) pour améliorer la lisibilité.
- **Layout** : grille 12 colonnes avec cartes en masonry (max 3 par ligne en desktop, 1 en mobile). Padding généreux (24–28px), ombres douces (blur 18px, opacité 10%).
- **Composants** :
  - Cartes stratégiques avec header compact (titre + badge), corps aligné à gauche, footer avec CTA primaire (dégradé magenta→turquoise) et CTA secondaire en outline clair.
  - Statistiques en mini cartes alignées (Chaud/Froid, Fréquences, Timeline) avec fond légèrement translucide (glassmorphism light : background rgba(255,255,255,0.06), bordure 1px rgba(255,255,255,0.1)).
  - Barre supérieure sticky : logo + sélecteur de jeu (Euromillion/Eurodream) + bouton "Lancer l'IA".
- **Micro-interactions** : hover qui relève l'ombre et augmente la saturation du dégradé; transitions 180ms; pastilles de numéros avec effet glass léger et border subtile.
- **Accessibilité** : contrastes WCAG AA pour texte (tests sur violet de fond vs blanc), taille de police minimum 15–16px, focus ring cyan.

## Direction 2 : Clean Minimal (accent data)
- **Palette** : fond gris très sombre (#0f1115), accents verts/menthe (#39d98a) et bleus (#4da3ff), surfaces en gris anthracite (#181b21).
- **Typo** : "Manrope" ou "Space Grotesk" pour un look fintech; titres 22–26px, labels uppercase 12px tracking +4%.
- **Layout** : deux colonnes principales en desktop (sélecteur + résumé à gauche, stratégies et stats à droite), passage en pile sur mobile. Grille de cartes plates avec coins à 12px et bordure 1px rgba(255,255,255,0.08).
- **Composants** :
  - En-tête clair : breadcrumb (Accueil > Stratégies), switch Euromillion/Eurodream, badge "Simulation".
  - Carte "Dernier tirage" en pleine largeur, chiffres en pastilles outlines, badge date.
  - Section "Stratégies" sous forme de listes denses avec toggles (chips) pour sélectionner la méthode; CTA principal unique en bas de page (éviter la surabondance de boutons).
  - Blocs "Insights" (Chaud/Froid, Fréquences) avec mini-graphes sparklines/heatmaps simplifiées.
- **Micro-interactions** : survol qui ajoute une bordure lumineuse menthe; transitions 150ms; focus visible.
- **Accessibilité** : contraste élevé, grandes zones cliquables, mode daltonien facilité par icônes + labels textuels.

## Approche de mise en œuvre
1) **Système de design** : définir une palette (JSON/SCSS variables), échelle de spacing, typographie, rayons et ombres; créer un fichier de tokens (ex: `styles/tokens.css`).
2) **Bibliothèque de composants** : cartes, boutons, badges, pastilles de numéros, chip de stratégie, en-tête sticky et grille responsive; idéalement en composant React ou Web Components, sinon HTML/CSS modulaires (BEM ou utility-first). 
3) **Hiérarchisation** : limiter les CTA primaires à 1–2 par écran; regrouper les stats dans des sections identifiables; ordre visuel clair (headline > sélecteur de jeu > stratégie > stats > action finale).
4) **Itérations** : prototyper rapidement en Figma (variants light/dark), tester contrastes (WCAG), puis intégrer avec un thème togglable (gradient vs minimal) en changeant uniquement les tokens.

## Recommandation
- Si vous souhaitez rester proche de l'existant : adoptez **Direction 1** avec des dégradés plus sobres, du glass léger et une typographie plus lisible.
- Si vous voulez un saut vers un look plus "fintech" et data-first : choisissez **Direction 2**, plus minimaliste et focalisé sur les insights, avec moins de distraction et une action principale claire.
