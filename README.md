# ICEF Berlin Meeting Briefs

Prep page for Arno's meetings at ICEF Berlin, 2–3 November 2026.

## How it works

- `data.py` — all the content. One Python dict per meeting: contact, links, badges, four bullets, the angle line, the students-per-year estimate, the profile-detail rows, and sources.
- `style.css` — the page styling.
- `build.py` — renders `data.py` into `index.html`.
- `index.html` — the built briefs page (committed so it can also be dropped onto any static host as-is).
- `data/signups_by_country.csv` + `signups.py` + `build_signups.py` — the **Signups by country** page (`signups.html`). To refresh it, replace the CSV (columns `country, signups, rank`) and update the snapshot date in `signups.py`.

## Updating the page

1. Edit `data.py` (fix a number, add a bullet, add or remove a meeting). Keep the quotes balanced; the file is plain Python.
2. Run `python3 build.py` locally, or just commit — the GitHub Action rebuilds `index.html` and redeploys on every push to `main`.

Editing `data.py` directly on github.com and committing is enough; no local setup needed.

## Hosting

Deployed by `.github/workflows/pages.yml` to GitHub Pages (Settings → Pages → Source: *GitHub Actions*).

To host elsewhere, upload `index.html` on its own; it has no other dependencies apart from Google Fonts.
