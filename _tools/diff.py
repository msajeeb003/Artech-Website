"""Pixel comparison of the replica screenshots (_tools/out) with the live-site captures.
   python _tools/diff.py [viewport ...]   -> prints a match percentage per section and
   writes <viewport>.diff.png (original | replica | differences in red)."""
import json, os, sys
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'site-research')
TOL = 24      # per-channel difference that still counts as "same" (image re-compression, anti-aliasing)
for vp in (sys.argv[1:] or ['desktop-1440', 'mobile-390']):
    a = Image.open(os.path.join(RESEARCH, 'screenshots', vp, 'full', 'home.png')).convert('RGB')
    b = Image.open(os.path.join(HERE, 'out', vp + '.png')).convert('RGB')
    h = min(a.height, b.height)
    d = ImageChops.difference(a.crop((0, 0, a.width, h)), b.crop((0, 0, a.width, h))).convert('L').point(lambda v: 255 if v > TOL else 0)
    secs = json.load(open(os.path.join(RESEARCH, 'data', 'sections', vp, 'home.json'), encoding='utf-8'))[1:]
    print(f'\n{vp}: original {a.size}, replica {b.size}')
    total = 0
    for s in secs:
        y0, y1 = round(s['y']), min(h, round(s['y'] + s['h']))
        hist = d.crop((0, y0, a.width, y1)).histogram()
        bad = hist[255]; n = a.width * (y1 - y0); total += bad
        print(f"  {s['label'][:42]:42} {100 - 100 * bad / n:6.2f}% match")
    print(f'  {"whole page":42} {100 - 100 * total / (a.width * h):6.2f}% match')
    red = Image.new('RGB', (a.width, h), (255, 0, 0))
    over = b.crop((0, 0, a.width, h)).point(lambda v: v // 3)
    over.paste(red, (0, 0), d)
    sheet = Image.new('RGB', (a.width * 3 + 20, h), (40, 40, 40))
    sheet.paste(a.crop((0, 0, a.width, h)), (0, 0)); sheet.paste(b.crop((0, 0, a.width, h)), (a.width + 10, 0)); sheet.paste(over, (2 * a.width + 20, 0))
    sheet.save(os.path.join(HERE, 'out', vp + '.diff.png'))
