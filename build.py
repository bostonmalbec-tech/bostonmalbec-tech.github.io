"""Arma index.html a partir de plantilla.html y videos.json.

Uso:
  python3 build.py                 # reconstruye la página
  python3 build.py add ID [ID...]  # agrega videos de YouTube (lee título y canal) y reconstruye
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(ROOT, 'plantilla.html')
DATA = os.path.join(ROOT, 'videos.json')
OUT = os.path.join(ROOT, 'index.html')
PLAY = '<div class="play"><span><svg viewBox="0 0 24 24"><path d="M6 4l14 8-14 8z"/></svg></span></div>'
e = html.escape


def curl(args):
    return subprocess.run(['curl', '-s', '-m', '20'] + args, capture_output=True, text=True).stdout


def fetch_youtube(vid):
    url = urllib.parse.quote(f'https://www.youtube.com/watch?v={vid}', safe='')
    d = json.loads(curl([f'https://www.youtube.com/oembed?url={url}&format=json']))
    short = curl(['-o', '/dev/null', '-w', '%{http_code}', f'https://www.youtube.com/shorts/{vid}']) == '200'
    return {
        'id': vid, 'platform': 'youtube', 'vertical': short, 'title': d['title'],
        'channel': d['author_name'], 'channel_url': d['author_url'],
        'tags': ['Edición', 'Short' if short else 'Gaming'],
        'url': f'https://www.youtube.com/shorts/{vid}' if short else f'https://www.youtube.com/watch?v={vid}',
    }


def tile(v):
    kind = 'v' if v['vertical'] else 'h'
    label = f'Reproducir: {v["title"]}'
    if v['platform'] == 'youtube':
        attr = f'data-yt="{e(v["id"])}" data-v="{1 if v["vertical"] else 0}"'
        badge = '<span class="badge">Short</span>' if v['vertical'] else ''
    else:
        attr = f'data-ig="{e(v["id"])}"'
        badge = '<span class="badge">Reel</span>'
    return (f'          <figure class="vid {kind}"><div class="frame" {attr} aria-label="{e(label)}">{badge}{PLAY}</div>'
            f'<figcaption><a href="{e(v["url"])}" target="_blank" rel="noopener">{e(v["title"])}</a></figcaption></figure>\n')


def build():
    videos = json.load(open(DATA, encoding='utf-8'))
    groups = {}
    for v in videos:
        groups.setdefault(v['channel'], []).append(v)

    stacks = ''
    for i, (chan, vs) in enumerate(groups.items()):
        n = len(vs)
        stacks += (f'      <article class="stack" style="--i:{i}">\n'
                   f'        <header class="stack-head"><span class="num">{i + 1:02d}</span>'
                   f'<div class="who"><span class="k upper">Cliente</span><h3>{e(chan)}</h3>'
                   f'<span class="count">{n} {"video" if n == 1 else "videos"}</span></div>'
                   f'<a class="btn-line upper" href="{e(vs[0]["channel_url"])}" target="_blank" rel="noopener">Ver canal ↗</a></header>\n'
                   f'        <div class="stack-body">\n' + ''.join(tile(v) for v in vs) + '        </div>\n'
                   f'      </article>\n')

    names = list(groups.keys())
    logos = ''.join(f'<span>{e(n)}</span>' for n in names)
    logos = logos + logos.replace('<span>', '<span aria-hidden="true">')

    yt = [v['id'] for v in videos if v['platform'] == 'youtube']
    def row(ids):
        t = ''.join(f'<div class="g-tile"><img src="https://i.ytimg.com/vi/{i}/hqdefault.jpg" alt="" loading="lazy" onerror="this.remove()"></div>' for i in ids)
        return t + t
    r1, r2 = yt[0::2], yt[1::2]

    s = open(TPL, encoding='utf-8').read()
    for k, val in {'%%STACKS%%': stacks, '%%LOGOS%%': logos, '%%GALLERY1%%': row(r1), '%%GALLERY2%%': row(r2),
                   '%%N_VIDEOS%%': str(len(videos)), '%%N_CLIENTS%%': str(len(groups))}.items():
        s = s.replace(k, val)
    assert '%%' not in s
    open(OUT, 'w', encoding='utf-8').write(s)
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
