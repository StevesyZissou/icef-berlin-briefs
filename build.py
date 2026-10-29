#!/usr/bin/env python3
"""Render the ICEF Berlin meeting-prep page from data.py."""
import html
import json
from pathlib import Path

from data import MEETINGS, META

HERE = Path(__file__).parent
OUT = HERE / "index.html"


def esc(s):
    return html.escape(str(s), quote=True)


def badge(text, cls=""):
    return f'<span class="badge {cls}">{esc(text)}</span>'


def render_links(links):
    out = []
    for label, url in links:
        href = url if url.startswith("http") else "https://" + url
        out.append(f'<a href="{esc(href)}" target="_blank" rel="noopener">{esc(label)}</a>')
    return " · ".join(out)


CONF_LABEL = {"high": "high", "medium": "medium", "low": "low", "na": "reach"}


def conf_pill(conf, suffix=""):
    return f'<span class="conf conf-{conf}">{esc(CONF_LABEL.get(conf, conf))}{suffix}</span>'


def render_index(day_label, items):
    rows = []
    for m in items:
        est = m["estimate"]["headline"]
        rows.append(
            f'<tr><td class="t">{esc(m["time"])}</td>'
            f'<td class="org"><a href="#{m["id"]}">{esc(m["org"])}</a>'
            f'<span class="sub">{esc(m["contact"]["name"])} · {esc(m["location"])}</span></td>'
            f'<td class="kind">{esc(m["kind"])}</td>'
            f'<td class="est"><span class="num">{esc(est)}</span>'
            f'{conf_pill(m["estimate"]["confidence"])}</td></tr>'
        )
    return (
        f'<div class="idx"><h3>{esc(day_label)}</h3>'
        '<div class="tablewrap"><table class="index">'
        '<thead><tr><th>Time</th><th>Who</th><th>Type</th><th>Students / yr</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></div>'
    )


def render_meeting(m, n):
    c = m["contact"]
    est = m["estimate"]
    bullets = "".join(f"<li>{b}</li>" for b in m["bullets"])
    badges = "".join(badge(b[0], b[1]) for b in m.get("badges", []))

    facts = ""
    if m.get("facts"):
        facts = '<dl class="facts">' + "".join(
            f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in m["facts"]
        ) + "</dl>"

    sources = ""
    if m.get("sources"):
        sources = '<p class="sources">Sources: ' + " · ".join(
            f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(l)}</a>' for l, u in m["sources"]
        ) + "</p>"

    contact_lines = [f'<strong>{esc(c["name"])}</strong>']
    if c.get("title"):
        contact_lines.append(esc(c["title"]))
    contact_meta = " · ".join(contact_lines)
    contact_bits = []
    for e in c.get("emails", []):
        contact_bits.append(f'<span class="mono sel">{esc(e)}</span>')
    if c.get("phone"):
        contact_bits.append(f'<span class="mono sel">{esc(c["phone"])}</span>')

    loc_note = f' <span class="locnote">{esc(m["loc_note"])}</span>' if m.get("loc_note") else ""

    return f"""
<article class="meeting" id="{m['id']}">
  <div class="rail">
    <div class="time mono">{esc(m['time'])}</div>
    <div class="day">{esc(m['day_short'])}</div>
    <div class="n mono">{n:02d}</div>
  </div>
  <div class="body">
    <header>
      <div class="kicker">{esc(m['location'])}{loc_note}</div>
      <h2>{esc(m['org'])}</h2>
      <div class="badges">{badges}</div>
      <div class="contact">
        <div class="who">{contact_meta}</div>
        <div class="bits">{" · ".join(contact_bits)}</div>
        <div class="links">{render_links(m['links'])}</div>
      </div>
    </header>
    <div class="grid">
      <div class="summary">
        <ul class="bullets">{bullets}</ul>
        {('<p class="angle"><span class="lbl">Angle</span>' + m['angle'] + '</p>') if m.get('angle') else ''}
      </div>
      <aside class="estimate">
        <div class="lbl">Students / year (est.)</div>
        <div class="num">{esc(est['headline'])}</div>
        <div class="range">{esc(est['range'])}</div>
        {conf_pill(est['confidence'], '' if est['confidence'] == 'na' else ' confidence')}
        <p class="basis">{est['basis']}</p>
      </aside>
    </div>
    <div class="more">
      <div class="lbl">Profile detail</div>
      {facts}
      {sources}
    </div>
  </div>
</article>"""


def main():
    css = (HERE / "style.css").read_text()
    mon = [m for m in MEETINGS if m["day"] == "mon"]
    tue = [m for m in MEETINGS if m["day"] == "tue"]
    cards = "".join(render_meeting(m, i + 1) for i, m in enumerate(MEETINGS))

    page = f"""<!doctype html>
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
<header class="masthead">
  <div class="eyebrow mono">{esc(META['eyebrow'])}</div>
  <h1>{esc(META['title'])}</h1>
  <p class="lede">{META['lede']}</p>
  <div class="stats">
    {''.join(f'<div class="stat"><div class="v mono">{esc(v)}</div><div class="k">{esc(k)}</div></div>' for k, v in META['stats'])}
  </div>
  <p class="howto">{META['howto']}</p>
</header>

<section class="indexes">
  {render_index('Monday, 2 November', mon)}
  {render_index('Tuesday, 3 November', tue)}
</section>

<section class="meetings">
  <h2 class="dayhead" id="monday">Monday, 2 November</h2>
  {''.join(render_meeting(m, i + 1) for i, m in enumerate(MEETINGS) if m['day'] == 'mon')}
  <h2 class="dayhead" id="tuesday">Tuesday, 3 November</h2>
  {''.join(render_meeting(m, i + 1) for i, m in enumerate(MEETINGS) if m['day'] == 'tue')}
</section>

<footer class="foot">
  <p>{META['footer']}</p>
</footer>
</div>
</body>
</html>
"""
    OUT.write_text(page)
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes), {len(MEETINGS)} meetings")


if __name__ == "__main__":
    main()
