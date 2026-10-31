📊 README vivant — GitHub Actions

Automatisation zéro LLM, zéro token, zéro ressource VPS : un workflow GitHub Actions régénère chaque jour un SVG (stats + derniers commits) et le committe dans le repo. Ton README affiche une carte toujours à jour.

Coût : gratuit sur repos publics (runners gratuits sans limite). Sur repo privé : ~1 min/jour ≈ 35 min/mois, largement sous les 2 000 minutes offertes par le plan Free.

Consommation API GitHub : ~7 requêtes/jour, sans token (limite 60 req/h) ou avec GITHUB_TOKEN (5000 req/h).



1. Le workflow — .github/workflows/live-readme.yml

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
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
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



2. Le script — scripts/generate_activity_svg.py

Python stdlib uniquement (aucun pip install), appelable aussi en local : OWNER=ton-pseudo python scripts/generate_activity_svg.py.

#!/usr/bin/env python3
"""Génère assets/github-activity.svg : carte d'activité pour un README vivant."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

OWNER = os.environ.get("OWNER") or os.environ.get("GITHUB_REPOSITORY", "x/y").split("/")[0]
TOKEN = os.environ.get("GITHUB_TOKEN")  # optionnel (repos publics)
API = "https://api.github.com"


def gh(path):
    req = urllib.request.Request(
        API + path,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "live-readme-bot"},
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    # 1. Tous les repos personnels (hors forks)
    repos = [r for r in gh(f"/users/{OWNER}/repos?per_page=100&type=owner")
             if not r["fork"]]

    stars = sum(r["stargazers_count"] for r in repos)
    forks = sum(r["forks_count"] for r in repos)
    issues = sum(r["open_issues_count"] for r in repos)

    # 2. Les 3 repos les plus récemment actifs + commits des 7 derniers jours
    since = (datetime.now(timezone.utc) - timedelta(days=7)
             ).strftime("%Y-%m-%dT%H:%M:%SZ")
    active = sorted(repos, key=lambda r: r["pushed_at"], reverse=True)[:3]

    weekly = 0
    lines = []
    for r in active:
        commits = gh(f"/repos/{OWNER}/{r['name']}/commits?per_page=100&since={since}")
        weekly += len(commits)
        last = gh(f"/repos/{OWNER}/{r['name']}/commits?per_page=1")[0]
        msg = esc(last["commit"]["message"].splitlines()[0][:46])
        lines.append((r["name"], msg))

    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    # 3. Construction du SVG
    fg, dim, accent, bg = "#e6edf3", "#8b949e", "#58a6ff", "#0d1117"
    rows = "\n".join(
        f'<text x="32" y="{250 + i * 34}" fill="{fg}" font-size="16">'
        f'<tspan fill="{accent}">{esc(name)}</tspan>'
        f'<tspan fill="{dim}" dx="10">·</tspan>'
        f'<tspan dx="10">{msg}</tspan></text>'
        for i, (name, msg) in enumerate(lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="560" height="390" viewBox="0 0 560 390">
  <rect width="560" height="390" rx="12" fill="{bg}"/>
  <rect x="24" y="24" width="70" height="4" rx="2" fill="{accent}"/>
  <text x="24" y="64" fill="{fg}" font-size="20" font-weight="600"
        font-family="Segoe UI, Helvetica, Arial, sans-serif">
    Activité GitHub — {esc(OWNER)}</text>
  <text x="536" y="64" text-anchor="end" fill="{dim}" font-size="13"
        font-family="Segoe UI, sans-serif">maj {today}</text>
  <text x="32" y="128" fill="{fg}" font-size="16" font-family="Segoe UI, sans-serif">
    <tspan font-size="28" font-weight="700">{stars}</tspan>
    <tspan fill="{dim}" dx="8" font-size="14">stars</tspan>
    <tspan dx="28" font-size="28" font-weight="700">{forks}</tspan>
    <tspan fill="{dim}" dx="8" font-size="14">forks</tspan>
    <tspan dx="28" font-size="28" font-weight="700">{issues}</tspan>
    <tspan fill="{dim}" dx="8" font-size="14">issues ouvertes</tspan>
    <tspan dx="28" font-size="28" font-weight="700">{weekly}</tspan>
    <tspan fill="{dim}" dx="8" font-size="14">commits / 7 j</tspan>
  </text>
  <line x1="24" y1="168" x2="536" y2="168" stroke="#30363d" stroke-width="1"/>
  <text x="32" y="204" fill="{dim}" font-size="14" font-family="Segoe UI, sans-serif">
    DERNIERS COMMITS</text>
  {rows}
</svg>
"""
    os.makedirs("assets", exist_ok=True)
    with open("assets/github-activity.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"SVG généré : {len(repos)} repos, {stars} stars, {weekly} commits/7j")


if __name__ == "__main__":
    main()



3. Dans le README du repo

## 📊 En direct de mon GitHub

![Activité GitHub](assets/github-activity.svg)



4. Mise en route (5 minutes)





Créer le fichier .github/workflows/live-readme.yml (section 1) sur la branche par défaut.



Créer scripts/generate_activity_svg.py (section 2).



Ajouter le bloc (section 3) au README.md.



Onglet Actions → workflow Live README → Run workflow pour tester immédiatement.



Vérifier que le SVG est commité et s'affiche dans le README.

Le workflow tourne ensuite tout seul chaque matin ; s'il n'y a aucun changement (aucun commit, stats identiques), rien n'est commité — l'historique reste propre.

5. Notes





Cache d'images GitHub (Camo) : GitHub met en cache les images du README. Le SVG se rafraîchit automatiquement au bout de quelques minutes à quelques heures après le commit. Pour tester, affiche directement assets/github-activity.svg dans le repo.



Dormance des workflows : GitHub désactive le cron d'un repo public sans activité depuis 60 jours — un push de temps en temps suffit à le garder actif.



Personnalisation : couleurs (variables fg, accent, bg), nombre de repos suivis ([:3]), fenêtre de commits (days=7) — tout se règle en tête de script, sans dépendance.

