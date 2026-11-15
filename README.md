📊 README vivant — GitHub Actions

# live-readme

Génère chaque jour un SVG d'activité GitHub (stats + derniers commits) et le committe dans `assets/github-activity.svg`, pour l'afficher dans un README.

## Contenu

- `.github/workflows/live-readme.yml` — workflow GitHub Actions « Live README » : déclenché chaque jour à 06:17 UTC (`cron: "17 6 * * *"`) et manuellement (`workflow_dispatch`) ; exécute le script puis committe le SVG s'il a changé.
- `scripts/generate_activity_svg.py` — script Python (stdlib uniquement) qui interroge l'API GitHub (repos du propriétaire, stars/forks/issues ouvertes, 3 repos les plus récents, commits des 7 derniers jours) et écrit `assets/github-activity.svg`. Variables d'env : `OWNER` (ou `GITHUB_REPOSITORY`), `GITHUB_TOKEN` optionnel.
- `assets/github-activity.svg` — le SVG généré, à référencer dans un README via `![...](assets/github-activity.svg)`.
- `.github/workflows/stale.yml` — configuration du bot actions/stale.
- `README.md` — ce fichier.

## Usage

Le workflow tourne sur les runners GitHub (aucune ressource locale). En local : `OWNER=<pseudo> python scripts/generate_activity_svg.py`.
