#!/usr/bin/env python3
"""Render signups.html from data/signups_by_country.csv."""
import html
import json
from pathlib import Path

from signups import META, MISCLICKS, load_rows, partner_markets

HERE = Path(__file__).parent


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(n):
    return f"{n:,}"


def compact(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n/1000:.0f}K"
    if n >= 1_000:
        return f"{n/1000:.1f}K"
    return str(n)


def build(css, nav):
    rows = load_rows()
    pm = partner_markets()
    total = sum(r["signups"] for r in rows)
    top = rows[0]["signups"]
    top10 = sum(r["signups"] for r in rows[:10])
    misclick_total = sum(r["signups"] for r in rows if r["country"] in MISCLICKS)
    n_partner = sum(1 for r in rows if r["country"] in pm)
    partner_total = sum(r["signups"] for r in rows if r["country"] in pm)

    trs = []
    for r in rows:
        c = r["country"]
        share = r["signups"] / total * 100
        width = r["signups"] / top * 100
        flags = []
        if c in MISCLICKS:
            flags.append('<span class="tag warn">likely mis-click</span>')
        partners = pm.get(c, [])
        if partners:
            links = ", ".join(f'<a href="index.html#{pid}">{esc(short)}</a>' for pid, short in partners)
            flags.append(f'<span class="tag partners" title="ICEF meeting partners recruiting here">{links}</span>')
        share_txt = f"{share:.1f}%" if share >= 0.05 else "<0.1%"
        trs.append(
            f'<tr data-country="{esc(c.lower())}" data-signups="{r["signups"]}" data-rank="{r["rank"]}"'
            f' data-partner="{1 if partners else 0}" data-misclick="{1 if c in MISCLICKS else 0}">'
            f'<td class="rank mono">{r["rank"]}</td>'
            f'<td class="country"><span class="name">{esc(c)}</span>{"".join(flags)}</td>'
            f'<td class="bar"><div class="track" title="{esc(c)}: {fmt(r["signups"])} signups ({share_txt})"><div class="fill" style="width:{width:.2f}%"></div></div></td>'
            f'<td class="num mono">{fmt(r["signups"])}</td>'
            f'<td class="share mono">{share_txt}</td></tr>'
        )

    notes = "".join(f"<li>{n}</li>" for n in META["notes"])
    stats = [
        ("Signups counted", fmt(total)),
        ("Countries", str(len(rows))),
        ("Top 10 share", f"{top10/total*100:.0f}%"),
        ("Partner markets", f"{n_partner} · {compact(partner_total)}"),
        ("Likely mis-clicks", compact(misclick_total)),
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(META['title'])}</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
html {{ color-scheme: light dark; }}
body {{ margin: 0; }}
img {{ max-width: 100%; }}
[hidden] {{ display: none !important; }}
{css}
</style>
</head>
<body>
<div class="page">
{nav}
<header class="masthead">
  <div class="eyebrow mono">{esc(META['eyebrow'])}</div>
  <h1>{esc(META['title'])}</h1>
  <p class="lede">{META['lede']}</p>
  <div class="stats">
    {''.join(f'<div class="stat"><div class="v mono">{esc(v)}</div><div class="k">{esc(k)}</div></div>' for k, v in stats)}
  </div>
  <ul class="notes">{notes}</ul>
</header>

<section class="controls" aria-label="Filter and sort">
  <label class="search"><span class="lbl">Find</span><input id="q" type="search" placeholder="Country name" autocomplete="off"></label>
  <div class="chips" role="group" aria-label="Show">
    <button class="chip is-on" data-filter="all" id="f-all">All countries</button>
    <button class="chip" data-filter="partner" id="f-partner" title="Countries at least one ICEF meeting partner recruits from">Partner markets</button>
    <button class="chip" data-filter="clean" id="f-clean">Hide likely mis-clicks</button>
  </div>
  <div class="count" id="count"></div>
</section>

<section class="tablewrap">
<table class="signups" id="tbl">
  <thead><tr>
    <th class="rank"><button class="sort" data-key="rank" data-dir="asc" id="s-rank">Rank</button></th>
    <th class="country"><button class="sort" data-key="country" data-dir="asc" id="s-country">Country</button></th>
    <th class="bar" aria-label="Signups relative to the top country"></th>
    <th class="num"><button class="sort is-on" data-key="signups" data-dir="desc" id="s-signups">Signups</button></th>
    <th class="share">Share</th>
  </tr></thead>
  <tbody>{''.join(trs)}</tbody>
</table>
</section>

<footer class="foot">
  <p>Source: Arno onboarding responses, exported 29 October 2026 (data/signups_by_country.csv in this repo). Partner-market tags come from the “Recruits from” line of each meeting brief.</p>
</footer>
</div>
<script>
(function () {{
  var q = document.getElementById('q');
  var tbody = document.querySelector('#tbl tbody');
  var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
  var count = document.getElementById('count');
  var filter = 'all';
  var sortKey = 'signups', sortDir = 'desc';

  function apply() {{
    var term = q.value.trim().toLowerCase();
    var shown = 0, sum = 0;
    rows.forEach(function (tr) {{
      var ok = true;
      if (term && tr.dataset.country.indexOf(term) === -1) ok = false;
      if (filter === 'partner' && tr.dataset.partner !== '1') ok = false;
      if (filter === 'clean' && tr.dataset.misclick === '1') ok = false;
      tr.hidden = !ok;
      if (ok) {{ shown++; sum += +tr.dataset.signups; }}
    }});
    count.textContent = shown + ' of ' + rows.length + ' countries · ' + sum.toLocaleString('en-US') + ' signups';
  }}

  function sort() {{
    var dir = sortDir === 'asc' ? 1 : -1;
    rows.sort(function (a, b) {{
      var x = a.dataset[sortKey], y = b.dataset[sortKey];
      if (sortKey !== 'country') {{ x = +x; y = +y; return (x - y) * dir || (+a.dataset.rank - +b.dataset.rank); }}
      return x.localeCompare(y) * dir;
    }});
    rows.forEach(function (tr) {{ tbody.appendChild(tr); }});
    document.querySelectorAll('.sort').forEach(function (b) {{
      var on = b.dataset.key === sortKey;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-sort', on ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none');
      b.dataset.dir = on ? sortDir : b.dataset.dir;
    }});
  }}

  q.addEventListener('input', apply);
  document.querySelectorAll('.chip').forEach(function (c) {{
    c.addEventListener('click', function () {{
      filter = c.dataset.filter;
      document.querySelectorAll('.chip').forEach(function (x) {{ x.classList.toggle('is-on', x === c); }});
      apply();
    }});
  }});
  document.querySelectorAll('.sort').forEach(function (b) {{
    b.addEventListener('click', function () {{
      if (sortKey === b.dataset.key) {{ sortDir = sortDir === 'asc' ? 'desc' : 'asc'; }}
      else {{ sortKey = b.dataset.key; sortDir = b.dataset.key === 'country' ? 'asc' : (b.dataset.key === 'rank' ? 'asc' : 'desc'); }}
      sort();
    }});
  }});
  sort(); apply();
}})();
</script>
</body>
</html>
"""
