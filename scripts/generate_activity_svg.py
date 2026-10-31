name: Live README

on:
  schedule:
    - cron: "17 6 * * *"   # tous les jours à 06:17 UTC = 07:17 heure de Paris
  workflow_dispatch:        # bouton "Run workflow" dans l'onglet Actions

permissions:
  contents: write

concurrency:
  group: live-readme
  cancel-in-progress: false

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Générer le SVG
        run: python scripts/generate_activity_svg.py
        env:
          OWNER: ${{ github.repository_owner }}
          # Token automatique : évite les limites de débit, rien à configurer
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Committer si le SVG a changé
        run: |
          git config user.name  "readme-bot"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add assets/github-activity.svg
          if ! git diff --cached --quiet; then
            git commit -m "chore: refresh live readme [skip ci]"
            git push
          fi
