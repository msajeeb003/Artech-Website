"""Reads the captured home page (site-research/raw/html-source/home.html) and writes
home-data.json: the copy and image references the replica is built from."""
import json, re, sys, os, html
from html.parser import HTMLParser
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'site-research', 'raw', 'html-source', 'home.html')
src = open(SRC, encoding='utf-8').read()

VOID = {'img', 'br', 'input', 'meta', 'link', 'hr', 'source'}
class Node:
    def __init__(s, tag, attrs, parent):
        s.tag, s.attrs, s.parent, s.kids = tag, attrs, parent, []
    def cls(s): return s.attrs.get('class', '').split()
    def find(s, c):
        out = []
        for k in s.kids:
            if isinstance(k, Node):
                if c in k.cls(): out.append(k)
                out += k.find(c)
        return out
    def text(s):
        return re.sub(r'\s+', ' ', ''.join(k if isinstance(k, str) else k.text() for k in s.kids)).strip()
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.root = Node('root', {}, None); s.cur = s.root
    def handle_starttag(s, t, a):
        n = Node(t, dict(a), s.cur); s.cur.kids.append(n)
        if t not in VOID: s.cur = n
    def handle_startendtag(s, t, a):
        s.cur.kids.append(Node(t, dict(a), s.cur))
    def handle_endtag(s, t):
        n = s.cur
        while n is not s.root and n.tag != t: n = n.parent
        if n is not s.root: s.cur = n.parent
    def handle_data(s, d):
        if s.cur.tag not in ('script', 'style'): s.cur.kids.append(d)
p = P(); p.feed(src); R = p.root

def one(n, c):
    r = n.find(c); return r[0] if r else None
def img(n, c):
    r = one(n, c); return unquote(r.attrs['src']) if r else None

data = {}
box = R.find('brands-loop_box')[0]
data['brands'] = [{'src': unquote(i.attrs['src']), 'n': [c for c in i.cls() if c.startswith('_')][0][1:]} for i in box.find('brands-loop_icon')]
data['services'] = [{'icon': img(c, 'icon-service'), 'title': one(c, 'heading-text_service').text(), 'text': one(c, 'description-card-service').text()} for c in R.find('content-item_services')]
data['service_bg'] = img(R, 'img-figure_services')
sliders = R.find('basic-swiper')
def slides(sw):
    out = []
    for s in sw.find('swiper-slide'):
        a = one(s, 'projects_content-wrapper')
        d = {'href': a.attrs['href'], 'img': img(s, 'image_projects'), 'title': one(s, 'title-text_projects').text(), 'text': one(s, 'description-text_projects').text()}
        cat = one(s, 'category-text')
        if cat: d['cat'] = cat.text(); d['time'] = one(s, 'text_time').text()
        out.append(d)
    return out
data['projects'] = slides(sliders[0]); data['posts'] = slides(sliders[1])
data['team'] = [{'img': img(t, 'member-avatar'), 'name': one(t, 'member-name').text(), 'role': one(t, 'member-role').text()} for t in R.find('team-item-wrap')]
data['process'] = [{'icon': img(c, 'icon-process'), 'title': one(c, 'heading-text_process').text(), 'text': one(c, 'description-card-process').text(),
                    'size': ([x for x in one(c, 'description-card-process').cls() if x.startswith('size-')] or [''])[0]} for c in R.find('content-item_process')]
data['reviews'] = [{'name': one(r, 'client-name_text').text(), 'role': one(r, 'client-position_text').text(), 'text': one(r, 'reviews_text').text()} for r in R.find('auto-height_content')]
data['misc'] = {k: img(R, c) for k, c in [('logo', 'image_brand'), ('hero', 'image-big_hero'), ('arrow', 'arrow-icon_hero'), ('chevron', 'icon_arrow'), ('stars', 'icon_stars'), ('about_bg', 'img-background_big')]}
data['counter_icons'] = [unquote(i.attrs['src']) for i in R.find('icon-section_counter')]
data['platforms'] = [{'href': a.attrs['href'], 'img': img(a, 'icon_benefits')} for a in R.find('link_platform')]
json.dump(data, open(os.path.join(os.path.dirname(__file__), 'home-data.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print({k: (len(v) if isinstance(v, list) else v) for k, v in data.items() if k != 'misc'})
