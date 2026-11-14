import os, json, urllib.request
USER = os.environ.get("GH_USER", "omarnagy122")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")
TEAL, PUR, BG, BG2, TXT = "#ffb347", "#6366f1", "#0b1020", "#121933", "#cbd5e1"
FONT = "'Fira Code','JetBrains Mono',Consolas,'Courier New',monospace"

def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={"User-Agent": "stats-gen", **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

langs = {}
try:
    u = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += chunk
        if len(chunk) < 100: break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    for r in own[:40]:
        try:
            for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
except Exception as e:
    print("API unavailable, writing placeholder:", e)
    u = {"public_repos": "-", "followers": "-", "following": "-"}
    stars = "-"
tot = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda x: -x[1])[:5]

tiles = [("REPOSITORIES", u["public_repos"]), ("STARS EARNED", stars), ("FOLLOWERS", u["followers"]), ("FOLLOWING", u["following"])]
t = ""
for i, (lab, val) in enumerate(tiles):
    x, y = (i % 2) * 250, (i // 2) * 105
    t += f'<g transform="translate({x},{y})"><rect width="235" height="90" rx="14" fill="{BG2}" stroke="{TEAL}" stroke-opacity="0.35" stroke-width="1.5"/><text x="20" y="38" font-family="{FONT}" font-size="12" fill="#6b7280" letter-spacing="2">{lab}</text><text x="20" y="72" font-family="{FONT}" font-size="30" font-weight="700" fill="url(#g)">{val}</text></g>'
b = ""
for i, (name, n) in enumerate(top):
    pct = n / tot * 100
    y = 44 + i * 34
    b += f'<text x="0" y="{y}" font-family="{FONT}" font-size="13" fill="{TXT}">{name}</text><rect x="120" y="{y-12}" width="260" height="10" rx="5" fill="{BG}"/><rect x="120" y="{y-12}" width="{max(pct*2.6,4):.0f}" height="10" rx="5" fill="url(#g)"/><text x="395" y="{y-2}" font-family="{FONT}" font-size="12" fill="#6b7280">{pct:.0f}%</text>'
if not top:
    b = f'<text x="0" y="60" font-family="{FONT}" font-size="13" fill="#6b7280">updates automatically</text>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 220" width="1000" height="220">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset="1" stop-color="#ff5e7e"/></linearGradient></defs>
<g transform="translate(0,5)">{t}</g>
<g transform="translate(540,5)"><rect x="-10" y="0" width="470" height="195" rx="14" fill="{BG2}" stroke="{PUR}" stroke-opacity="0.5" stroke-width="1.5"/><g transform="translate(14,0)"><text y="28" font-family="{FONT}" font-size="12" fill="#6b7280" letter-spacing="2">TOP LANGUAGES</text>{b}</g></g>
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", u["public_repos"], stars, top)
