"""Genera el portafolio (una sola página larga, estilo presentación) a partir de videos.json.

Uso:
  python3 build.py                 # reconstruye la página
  python3 build.py add ID [ID...]  # agrega videos de YouTube (lee título y canal) y reconstruye
"""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'videos.json')
SITE = 'https://bostonmalbec-tech.github.io/'
YEAR = '2026'
WA = '523314516580'
WA_SHOW = '+52 33 1451 6580'
IG = 'bostonmori'
MAIL = 'bostonmalbec@gmail.com'
e = html.escape
PLAY = '<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 4.5v15l12.5-7.5z"/></svg></span>'
HANDLES = '<i class="h tl"></i><i class="h tr"></i><i class="h bl"></i><i class="h br"></i>'
# Cursor de flecha y manita en pixel art (originales)
ARROW = ('<svg class="px-cursor arrow" viewBox="0 0 12 19" aria-hidden="true" shape-rendering="crispEdges">'
         '<path fill="#111" d="M0 0h1v1h1v1h1v1h1v1h1v1h1v1h1v1h1v1h1v1h1v1h-4v1h1v2h1v2h1v1h-2v1h-2v-2h-1v-2h-1v-1h-1v1h-1v1h-1v1h-1z"/>'
         '<path fill="#fff" d="M1 2h1v1h1v1h1v1h1v1h1v1h1v1h1v1h1v1h1v1h-3v1h1v2h1v2h-1v-2h-1v-2h-2v1h-1v1h-1v1h-1z"/></svg>')
HAND = ('<svg class="px-cursor hand" viewBox="0 0 17 19" aria-hidden="true" shape-rendering="crispEdges">'
        '<path fill="#111" d="M5 0h2v1h1v5h2v1h2v1h2v1h1v1h1v5h-1v2h-1v1h-1v2h-8v-2h-1v-1h-1v-1h-1v-1h-1v-1h-1v-3h3v1h1v-9h1z"/>'
        '<path fill="#fff" d="M5 1h2v6h1v-1h2v1h1v1h1v-1h1v1h1v1h1v5h-1v2h-1v1h-1v2h-6v-2h-1v-1h-1v-1h-1v-1h-1v-1h-1v-1h2v1h1v1h1v-10z"/></svg>')

SERVICES = ['Corte y ritmo', 'Subtítulos dinámicos', 'Color', 'Sonido', 'Motion graphics', 'Entrega por formato']
TOOLS = [('Pr', 'Premiere Pro', 'pr'), ('Ae', 'After Effects', 'ae'), ('Dv', 'DaVinci Resolve', 'dv'), ('Cc', 'CapCut', 'cc')]
# Estilos tipográficos para el muro de creadores (cada nombre como si fuera su logo)
WORDMARKS = ['wm-a', 'wm-b', 'wm-c', 'wm-d', 'wm-e', 'wm-f', 'wm-g', 'wm-h', 'wm-i']


# ---------- datos ----------
def curl(args):
    return subprocess.run(['curl', '-s', '-m', '20'] + args, capture_output=True, text=True).stdout


def fetch_youtube(vid):
    url = urllib.parse.quote(f'https://www.youtube.com/watch?v={vid}', safe='')
    d = json.loads(curl([f'https://www.youtube.com/oembed?url={url}&format=json']))
    short = curl(['-o', '/dev/null', '-w', '%{http_code}', f'https://www.youtube.com/shorts/{vid}']) == '200'
    return {'id': vid, 'platform': 'youtube', 'vertical': short, 'title': d['title'],
            'channel': d['author_name'], 'channel_url': d['author_url'],
            'tags': ['Edición', 'Short' if short else 'Gaming'],
            'url': f'https://www.youtube.com/shorts/{vid}' if short else f'https://www.youtube.com/watch?v={vid}'}


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'creador'


def thumb(v, size='best'):
    if v['platform'] != 'youtube':
        return None
    if size == 'best':
        size = 'oar' if v['vertical'] else 'max'
    name = {'hq': 'hqdefault', 'max': 'maxresdefault', 'oar': 'oar2'}[size]
    return f'https://i.ytimg.com/vi/{v["id"]}/{name}.jpg'


def img(v, cls='', lazy=True):
    t = thumb(v)
    if not t:
        return f'<span class="ph {cls}"><span>Reel</span></span>'
    c = ' '.join(x for x in [cls, 'v' if v['vertical'] else ''] if x)
    lz = 'loading="lazy" ' if lazy else ''
    return (f'<img class="{c}" src="{t}" data-fallback="{thumb(v, "hq")}" alt="" '
            f'{lz}decoding="async" '
            f'onload="window.__thumbLoad&&__thumbLoad(this)" onerror="window.__thumbErr&&__thumbErr(this)">')


def ver(path):
    return hashlib.md5(open(os.path.join(ROOT, path), 'rb').read()).hexdigest()[:8]


# ---------- página ----------
def clip(v):
    attr = f'data-yt="{e(v["id"])}"' if v['platform'] == 'youtube' else f'data-ig="{e(v["id"])}"'
    ratio = 'v' if (v['vertical'] or v['platform'] == 'instagram') else 'h'
    return (f'<figure class="clip {ratio} reveal"><div class="frame" {attr} role="button" tabindex="0" '
            f'aria-label="Reproducir: {e(v["title"])}">{img(v)}{PLAY}</div>'
            f'<figcaption><span>{e(v["title"])}</span><a href="{e(v["url"])}" target="_blank" rel="noopener">Abrir ↗</a></figcaption></figure>')


def build():
    videos = json.load(open(DATA, encoding='utf-8'))
    groups = {}
    for v in videos:
        groups.setdefault(v['channel'], []).append(v)
    yt = [v for v in videos if v['platform'] == 'youtube' and not v['vertical']]

    slides = ''.join(f'<img class="slide{" on" if i == 0 else ""}" src="{thumb(v)}" data-fallback="{thumb(v, "hq")}" alt="" '
                     f'onload="window.__thumbLoad&&__thumbLoad(this)" onerror="window.__thumbErr&&__thumbErr(this)">' for i, v in enumerate(yt))
    collage = ''.join(f'<span class="cl cl{i}">{img(v, lazy=False)}</span>' for i, v in enumerate(yt[:5]))
    wall = ''.join(f'<a class="wm {WORDMARKS[i % len(WORDMARKS)]} reveal" href="#{slug(c)}" style="--i:{i}">{e(c)}</a>' for i, c in enumerate(groups))
    tools = ''.join(f'<span class="tool {k}" title="{e(name)}"><b>{ab}</b><small>{e(name)}</small></span>' for ab, name, k in TOOLS)
    svc = ''.join(f'<li>{e(s)}</li>' for s in SERVICES)

    works = ''
    for chan, vs in groups.items():
        n = len(vs)
        works += f'''
<section class="work" id="{slug(chan)}">
  <div class="divider reveal"><span class="tw">Trabajo para</span> <a class="who" href="{e(vs[0]["channel_url"])}" target="_blank" rel="noopener">{e(chan)}</a><span class="count">{n} {"video" if n == 1 else "videos"}</span></div>
  <div class="clips">{''.join(clip(v) for v in vs)}</div>
</section>'''

    page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Portafolio · Boston, editor de video</title>
<meta name="description" content="Portafolio de Boston, editor de video y motion graphics de Guadalajara, México: YouTube, reels, TikTok y Shorts.">
<meta property="og:title" content="Portafolio · Boston, editor de video">
<meta property="og:description" content="Casi 5 años editando videos para creadores de contenido. Mira mis trabajos.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og-image.png?v=7">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}og-image.png?v=7">
<link rel="icon" type="image/png" href="img/oso.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rozha+One&family=Instrument+Serif:ital@0;1&family=Courier+Prime:wght@400;700&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/styles.css?v={ver("assets/styles.css")}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>

<nav class="nav" aria-label="Secciones">
  <a class="brand" href="#inicio">Boston</a>
  <a href="#trabajos">Trabajos</a>
  <a href="#sobre-mi">Sobre mí</a>
  <a href="#contacto">Contacto</a>
</nav>

<section class="cover" id="inicio">
  <div class="clouds" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
  <p class="kicker">Edición de video, motion graphics y Shorts</p>
  <h1 class="mega"><span>PORTAFOLIO</span></h1>
  <div class="tv" aria-label="Televisión retro mostrando mis videos">
    <div class="tv-body">
      <div class="tv-screen">{slides}<span class="scan" aria-hidden="true"></span><span class="rec" aria-hidden="true">● REC</span></div>
      <div class="tv-panel" aria-hidden="true"><span class="knob"></span><span class="knob small"></span><span class="grill"></span></div>
    </div>
    <div class="tv-feet" aria-hidden="true"><i></i><i></i></div>
  </div>
  <svg class="grass" viewBox="0 0 1440 260" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="gr1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7CC95A"/><stop offset="1" stop-color="#2E7D2A"/></linearGradient>
      <linearGradient id="gr2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9BDB6E"/><stop offset="1" stop-color="#3E9334"/></linearGradient>
      <pattern id="blades" width="14" height="40" patternUnits="userSpaceOnUse"><path d="M2 40 L5 6 L7 40 M8 40 L11 12 L13 40" fill="#2B6E25" opacity=".35"/></pattern>
    </defs>
    <path d="M0 120 C240 70 420 110 720 90 C1020 70 1220 110 1440 80 L1440 260 L0 260Z" fill="url(#gr2)"/>
    <path d="M0 160 C300 120 520 150 760 135 C1040 118 1240 150 1440 128 L1440 260 L0 260Z" fill="url(#gr1)"/>
    <rect y="120" width="1440" height="140" fill="url(#blades)"/>
  </svg>
  <p class="cover-sign">Boston · Editor de video · Guadalajara, México</p>
</section>

<section class="looking">
  <div class="glass reveal">
    <p class="serif-xl"><em>¿Buscas</em></p>
    <p class="looking-sub">un editor de video, motion graphics<br>o alguien que haga tus Shorts…?</p>
  </div>
</section>

<section class="about" id="sobre-mi">
  <div class="about-visual reveal">
    <div class="collage" aria-hidden="true">{collage}<span class="vinyl"></span><span class="mini-tool pr">Pr</span><span class="mini-tool ae">Ae</span></div>
    <img class="bear" src="img/oso.png" alt="Oso polar con audífonos y claqueta, la mascota de Boston" width="900" height="900">
    {ARROW}
  </div>
  <div class="about-text">
    <div class="sel title-box reveal">{HANDLES}<h2 class="serif-l"><em>Sobre mí</em></h2></div>
    <div class="sel text-box reveal">{HANDLES}<p>Soy Boston, editor de video y motion graphics de Guadalajara, México. Llevo casi 5 años editando para creadores de contenido: gaming, vlogs y entretenimiento para YouTube, reels, TikTok y Shorts. Cuido cada corte, subtítulo y sonido para que la gente se quede hasta el final.</p></div>
    <ul class="services reveal">{svc}</ul>
    <div class="tools reveal">{tools}</div>
  </div>
</section>

<section class="brands" id="trabajos">
  <div class="sel dashed brands-title reveal">{HANDLES}<h2><em class="serif-i">Creadores</em> con los que he trabajado</h2>{HAND}</div>
  <div class="wall">{wall}</div>
</section>
{works}

<section class="thanks" id="contacto">
  <h2 class="typewrite" data-text="Gracias por ver"><span class="tw-text">Gracias por ver</span><span class="caret" aria-hidden="true">|</span></h2>
  <p class="thanks-sub reveal">¿Hacemos tu próximo video? Escríbeme y respondo en menos de 24 horas.</p>
  <div class="contact reveal">
    <a class="btn dark" href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp · {WA_SHOW}</a>
    <a class="btn" href="https://www.instagram.com/{IG}/" target="_blank" rel="noopener">Instagram · @{IG}</a>
    <a class="btn" href="mailto:{MAIL}">{MAIL}</a>
  </div>
</section>

<footer class="foot">©{YEAR} Boston · Editor de video</footer>
<script src="assets/app.js?v={ver("assets/app.js")}" defer></script>
</body>
</html>
'''
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    # Quitar las páginas del diseño anterior
    for old in ['sobre-mi.html', 'trabajos.html', 'contacto.html']:
        p = os.path.join(ROOT, old)
        if os.path.exists(p):
            os.remove(p)
    if os.path.isdir(os.path.join(ROOT, 'trabajos')):
        shutil.rmtree(os.path.join(ROOT, 'trabajos'))
    print(f'{len(videos)} videos · {len(groups)} creadores')


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'add':
        videos = json.load(open(DATA, encoding='utf-8'))
        have = {v['id'] for v in videos}
        for vid in sys.argv[2:]:
            if vid in have:
                print('ya estaba:', vid)
                continue
            v = fetch_youtube(vid)
            videos.append(v)
            print('agregado:', 'SHORT' if v['vertical'] else '16:9', '|', v['title'], '|', v['channel'])
        json.dump(videos, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    build()
