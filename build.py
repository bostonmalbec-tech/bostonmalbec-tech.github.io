"""Genera el portafolio (varias páginas) a partir de videos.json.

Uso:
  python3 build.py                 # reconstruye todas las páginas
  python3 build.py add ID [ID...]  # agrega videos de YouTube (lee título y canal) y reconstruye
"""
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'videos.json')
SITE = 'https://bostonmalbec-tech.github.io/'
YEAR = '2026'
WA = '523314516580'
WA_SHOW = '+52 33 1451 6580'
IG = 'bostonmori'
MAIL = 'bostonmalbec@gmail.com'
FEATURED_CHANNEL = 'Willyrex'
e = html.escape
PLAY = '<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 4.5v15l12.5-7.5z"/></svg></span>'

SERVICES = ['Corte y ritmo', 'Subtítulos dinámicos', 'Color', 'Sonido', 'Motion graphics', 'Entrega por formato']
TOOLS = ['Premiere Pro', 'After Effects', 'DaVinci Resolve', 'CapCut']
PROCESS = ['Brief y material en bruto', 'Primer corte en 48 horas', '2 rondas de cambios', 'Entrega en máxima calidad']


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


def category(v):
    for t in v['tags']:
        if t not in ('Edición',):
            return t
    return 'Edición'


def kind(v):
    if v['platform'] == 'instagram':
        return 'Reel'
    return 'Short' if v['vertical'] else 'YouTube'


def thumb(v, size='best'):
    if v['platform'] != 'youtube':
        return None
    if size == 'best':
        size = 'oar' if v['vertical'] else 'max'
    name = {'hq': 'hqdefault', 'max': 'maxresdefault', 'oar': 'oar2'}[size]
    return f'https://i.ytimg.com/vi/{v["id"]}/{name}.jpg'


def img(v, cls='', size='best', lazy=True):
    t = thumb(v, size)
    if not t:
        return f'<span class="ph {cls}"><span>Reel</span></span>'
    vcls = (' ' + cls if cls else '') + (' v' if v['vertical'] else '')
    return (f'<img class="{vcls.strip()}" src="{t}" data-fallback="{thumb(v, "hq")}" alt="" '
            f'{"loading=\"lazy\" " if lazy else ""}decoding="async" onload="window.__thumbLoad&&__thumbLoad(this)" onerror="window.__thumbErr&&__thumbErr(this)">')


# ---------- piezas compartidas ----------
def head(title, desc, base, path=''):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}og-image.png?v=6">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}og-image.png?v=6">
<link rel="icon" type="image/png" href="{base}img/oso.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{base}assets/styles.css">
<script>document.documentElement.classList.add('js')</script>
</head>
'''


def header(base, active):
    def pill(href, label, key):
        cur = ' aria-current="page"' if key == active else ''
        return f'<a class="pill" href="{base}{href}"{cur}>{label}</a>'
    return f'''<header class="top">
  <a class="brand" href="{base}index.html">Boston</a>
  <nav class="mid" aria-label="Secciones">{pill("sobre-mi.html", "Sobre mí", "about")}{pill("trabajos.html", "Trabajos", "work")}{pill("contacto.html", "Contacto", "contact")}</nav>
  <nav class="side" aria-label="Redes"><a class="pill" href="https://www.instagram.com/{IG}/" target="_blank" rel="noopener">Instagram</a><a class="pill" href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp</a></nav>
</header>
'''


def footer(base):
    return f'''<footer class="foot">©{YEAR} Boston · Editor de video</footer>
<script src="{base}assets/app.js" defer></script>
</body>
</html>
'''


def frame(v):
    if v['platform'] == 'youtube':
        attr = f'data-yt="{e(v["id"])}"'
    else:
        attr = f'data-ig="{e(v["id"])}"'
    ratio = 'v' if v['vertical'] or v['platform'] == 'instagram' else 'h'
    return (f'<figure class="clip {ratio} reveal"><div class="frame" {attr} role="button" tabindex="0" '
            f'aria-label="Reproducir: {e(v["title"])}">{img(v)}{PLAY}</div>'
            f'<figcaption><span>{e(v["title"])}</span><a href="{e(v["url"])}" target="_blank" rel="noopener">Abrir ↗</a></figcaption></figure>')


# ---------- páginas ----------
def page_home(videos, groups):
    feat_chan = FEATURED_CHANNEL if FEATURED_CHANNEL in groups else next(iter(groups))
    feat = next(v for v in groups[feat_chan] if v['platform'] == 'youtube')
    others = [v for v in videos if v is not feat and v['platform'] == 'youtube'][:8]
    # posiciones de las miniaturas flotantes (x, y en % del escenario, ancho en vw, profundidad, giro)
    slots = [(-41, -9, 4.2, .9, 26), (-37, -3, 5.4, .7, 22), (-27, -12, 2.6, 1, 18), (-22.5, -2, 7.6, .45, 12),
             (22.5, -2, 7.2, .45, -12), (27.5, -11, 2.4, 1, -18), (33, -4, 3.6, .8, -22), (37.5, -7, 3.4, .95, -26)]
    floats = ''
    for i, (v, (x, y, w, d, r)) in enumerate(zip(others, slots)):
        floats += (f'<a class="float" href="trabajos/{slug(v["channel"])}.html" style="--x:{x}%;--y:{y}%;--w:{w}vw;--d:{d};--r:{r}deg;--i:{i + 2}" '
                   f'data-depth="{d}" aria-label="{e(v["channel"])}: {e(v["title"])}">{img(v, "", lazy=False)}</a>\n      ')
    return (head('Boston · Editor de video', 'Portafolio de Boston, editor de video de Guadalajara, México: YouTube, reels, TikTok y Shorts.', '', '')
            + '<body class="home">\n' + header('', 'home') + f'''<main class="stage" aria-label="Proyecto destacado">
  <div class="scene">
      {floats}<article class="feature" data-depth=".25" style="--i:1">
        <div class="bar"><span>{e(feat_chan)}</span><a class="pill dark" href="trabajos/{slug(feat_chan)}.html">Ver caso</a></div>
        <a class="cover" href="trabajos/{slug(feat_chan)}.html" aria-label="Ver caso de {e(feat_chan)}">
          {img(feat, "bg", lazy=False)}
          <span class="inset" data-depth="1.1">{img(feat, "", lazy=False)}</span>
        </a>
      </article>
  </div>
  <p class="tagline">Editor de video · Guadalajara, México · Casi 5 años haciendo videos que la gente ve hasta el final</p>
</main>
''' + footer(''))


def page_about(videos, groups):
    clients = ''.join(f'<li><a href="trabajos/{slug(c)}.html">{e(c)}</a></li>' for c in groups)
    lis = lambda xs: ''.join(f'<li>{e(x)}</li>' for x in xs)
    return (head('Sobre mí · Boston', 'Boston, editor de video en Guadalajara, México.', '', 'sobre-mi.html')
            + '<body>\n' + header('', 'about') + f'''<main class="page about">
  <p class="lede reveal">Soy Boston, editor de video en Guadalajara, México. Llevo casi cinco años convirtiendo horas de grabación en videos que la gente ve hasta el final: gaming, vlogs y entretenimiento para YouTube, reels, TikTok y Shorts. Trabajo con pocos proyectos a la vez para cuidar cada corte.</p>
  <div class="about-grid">
    <figure class="portrait reveal"><img src="img/oso.png" alt="Oso polar con audífonos y claqueta, la mascota de Boston" width="900" height="900"></figure>
    <div class="lists">
      <section class="reveal"><h2>Servicios</h2><ul>{lis(SERVICES)}</ul></section>
      <section class="reveal"><h2>Clientes</h2><ul>{clients}</ul></section>
      <section class="reveal"><h2>Herramientas</h2><ul>{lis(TOOLS)}</ul></section>
      <section class="reveal"><h2>Cómo trabajo</h2><ul>{lis(PROCESS)}</ul></section>
    </div>
  </div>
</main>
''' + footer(''))


def page_work(videos):
    cats = ['YouTube', 'Shorts y Reels'] + [c for c, _ in Counter(category(v) for v in videos if category(v) not in ('Short', 'Reel')).most_common()]
    def keys(v):
        k = ['todos', 'youtube' if kind(v) == 'YouTube' else 'shorts-y-reels', slug(category(v))]
        return ' '.join(dict.fromkeys(k))
    pills = '<button class="pill" type="button" data-filter="todos" aria-pressed="true">Todos</button>' + ''.join(
        f'<button class="pill" type="button" data-filter="{slug(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)
    tiles = ''
    for v in videos:
        tiles += (f'<a class="tile reveal" href="trabajos/{slug(v["channel"])}.html" data-cats="{keys(v)}">'
                  f'<span class="img">{img(v)}</span>'
                  f'<span class="label"><span class="name">{e(v["title"])}</span><span class="cat">{e(v["channel"])}</span></span></a>\n    ')
    return (head('Trabajos · Boston', 'Videos que Boston editó para creadores de contenido.', '', 'trabajos.html')
            + '<body>\n' + header('', 'work') + f'''<main class="page work">
  <h1 class="title reveal">Trabajos</h1>
  <div class="filters reveal" role="group" aria-label="Filtrar trabajos">{pills}</div>
  <div class="grid">
    {tiles}</div>
</main>
''' + footer(''))


def page_contact():
    return (head('Contacto · Boston', 'Escríbele a Boston para editar tu próximo video.', '', 'contacto.html')
            + '<body>\n' + header('', 'contact') + f'''<main class="page contact">
  <div class="contact-main">
    <p class="lede reveal">Hablemos de tu próximo video. Cuéntame qué estás creando.</p>
    <form class="form reveal" id="contact-form" data-wa="{WA}" novalidate>
      <label for="f-name">Nombre</label>
      <input id="f-name" name="nombre" type="text" placeholder="Tu nombre o el de tu canal" autocomplete="name" required>
      <label for="f-reach">WhatsApp o correo</label>
      <input id="f-reach" name="contacto" type="text" placeholder="Para responderte" autocomplete="email">
      <label for="f-msg">Detalles del proyecto</label>
      <textarea id="f-msg" name="detalles" rows="4" placeholder="Tipo de video, duración, fecha de entrega y presupuesto." required></textarea>
      <button class="submit" type="submit">Enviar por WhatsApp</button>
      <p class="form-note" id="form-note" role="status"></p>
    </form>
    <p class="aside reveal">¿Tienes un proyecto en mente? Me encantaría escucharlo.<br>Respondo en menos de 24 horas.</p>
  </div>
  <aside class="connect reveal">
    <h2>Contacto</h2>
    <a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp {WA_SHOW}</a>
    <a href="https://www.instagram.com/{IG}/" target="_blank" rel="noopener">Instagram @{IG}</a>
    <a href="mailto:{MAIL}">{MAIL}</a>
  </aside>
</main>
''' + footer(''))


def page_case(chan, vs):
    n = len(vs)
    cat = Counter(category(v) for v in vs).most_common(1)[0][0]
    plat = ', '.join(dict.fromkeys('Instagram Reels' if v['platform'] == 'instagram' else ('YouTube Shorts' if v['vertical'] else 'YouTube') for v in vs))
    fmt = ', '.join(dict.fromkeys('9:16' if (v['vertical'] or v['platform'] == 'instagram') else '16:9' for v in vs))
    what = {'Gaming': 'videos de gaming', 'Vlog': 'vlogs', 'Entretenimiento': 'videos de entretenimiento',
            'Short': 'contenido corto', 'Reel': 'contenido corto'}.get(cat, 'videos')
    clips = ''.join(frame(v) for v in vs)
    return (head(f'{chan} · Boston', f'Videos que Boston editó para {chan}.', '../', f'trabajos/{slug(chan)}.html')
            + '<body>\n' + header('../', 'work') + f'''<main class="page case">
  <div class="case-info">
    <h1 class="title reveal">{e(chan)}</h1>
    <p class="sub reveal">Edición de {what} para {e(plat)}.</p>
    <p class="desc reveal">Edité {n} {"video" if n == 1 else "videos"} para {e(chan)}: cortes con ritmo y un acabado listo para publicar, para que la gente se quede hasta el final.</p>
    <dl class="meta reveal">
      <div><dt>Cliente</dt><dd>{e(chan)}</dd></div>
      <div><dt>Plataforma</dt><dd>{e(plat)}</dd></div>
      <div><dt>Formato</dt><dd>{e(fmt)}</dd></div>
      <div><dt>Videos</dt><dd>{n}</dd></div>
    </dl>
    <div class="case-links reveal"><a class="pill dark" href="{e(vs[0]["channel_url"])}" target="_blank" rel="noopener">Ver canal ↗</a><a class="pill" href="../trabajos.html">Todos los trabajos</a></div>
  </div>
  <div class="case-media">{clips}</div>
</main>
''' + footer('../'))


def build():
    videos = json.load(open(DATA, encoding='utf-8'))
    groups = {}
    for v in videos:
        groups.setdefault(v['channel'], []).append(v)
    out = {'index.html': page_home(videos, groups), 'sobre-mi.html': page_about(videos, groups),
           'trabajos.html': page_work(videos), 'contacto.html': page_contact()}
    for chan, vs in groups.items():
        out[f'trabajos/{slug(chan)}.html'] = page_case(chan, vs)
    os.makedirs(os.path.join(ROOT, 'trabajos'), exist_ok=True)
    keep = set(out)
    for f in os.listdir(os.path.join(ROOT, 'trabajos')):
        if f'trabajos/{f}' not in keep and f.endswith('.html'):
            os.remove(os.path.join(ROOT, 'trabajos', f))
    for path, s in out.items():
        open(os.path.join(ROOT, path), 'w', encoding='utf-8').write(s)
    print(f'{len(videos)} videos · {len(groups)} creadores · {len(out)} páginas')


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
