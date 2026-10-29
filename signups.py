# Arno signups by country: data loading, partner-market mapping, and page metadata.
# Source file: data/signups_by_country.csv (country, signups, rank). Replace the CSV and rebuild to update.

import csv
import re
from pathlib import Path

from data import MEETINGS

HERE = Path(__file__).parent
CSV = HERE / "data" / "signups_by_country.csv"

META = {
    "title": "Arno Signups by Country",
    "eyebrow": "Arno · onboarding data · snapshot 29 October 2026",
    "lede": "Where Arno's signups say they live, ranked by country. Use it to size a partner's home market before the meeting.",
    "notes": [
        "Source is the onboarding answer to <em>Where do you live?</em>, so the ~70,000 users who skipped that question are not counted.",
        "Counts include teachers and agencies as well as students: most users never answered the role question, so they can't be filtered out reliably.",
        "Tied countries share a rank.",
        "A few entries are almost certainly dropdown mis-clicks rather than real users: American Samoa (next to “America” at the top of the list), British Indian Ocean Territory, Antarctica and Bouvet Island. They are flagged in the table.",
    ],
}

# Entries that are almost certainly dropdown mis-clicks.
MISCLICKS = {"American Samoa", "British Indian Ocean Territory", "Antarctica", "Bouvet Island"}

# Names used in the meeting briefs → names used in the signups CSV.
ALIASES = {
    "CAR": "Central African Republic",
    "UAE": "United Arab Emirates",
    "Vietnam": "Viet Nam",
    "Russia": "Russian Federation",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Türkiye": "Turkey",
    "UK": "United Kingdom of Great Britain and Northern Ireland",
    "USA": "United States of America",
    "DACH": None,
    "Germany/DACH in practice": "Germany",
}


def load_rows():
    rows = []
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({"country": r["country"], "signups": int(r["signups"]), "rank": int(r["rank"])})
    rows.sort(key=lambda r: (r["rank"], r["country"]))
    return rows


def partner_markets():
    """Map country -> list of (meeting id, org short name) whose 'Recruits from' line names it."""
    out = {}
    for m in MEETINGS:
        line = next((v for k, v in m.get("facts", []) if k == "Recruits from"), "")
        if not line:
            continue
        # Pull every parenthetical and the main clause alike; split on commas / semicolons / slashes.
        text = line.replace("(profile also lists", ",").replace("(profile:", ",").replace("(profile)", "")
        text = re.sub(r"\b(in practice|office clearly active too|profile)\b", "", text)
        parts = re.split(r"[,;()]", text)
        for p in parts:
            name = p.strip().strip(".").strip()
            if not name:
                continue
            if name in ALIASES:
                name = ALIASES[name]
            if not name:
                continue
            if "/" in name:
                name = name.split("/")[0].strip()
                name = ALIASES.get(name, name)
            short = m["org"].split(" (")[0].split(" – ")[0].split(" - ")[0]
            out.setdefault(name, [])
            if (m["id"], short) not in out[name]:
                out[name].append((m["id"], short))
    return out
