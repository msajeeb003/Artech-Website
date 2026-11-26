"""Builds the replica's index.html and asset folder.

    python _tools/extract.py     # read the captured page -> home-data.json
    python _tools/build.py       # copy/optimise assets, write index.html

Repeating blocks (22 project cards, 100 post cards, 12 logos x 3) come from
home-data.json; everything else is written out below by hand. The output is a
plain static page: once index.html exists, this script is not needed to run it.
"""
import json, os, re, shutil, sys
from html import escape
from urllib.parse import unquote
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
RESEARCH = os.path.join(os.path.dirname(OUT), 'site-research')
IMG = os.path.join(OUT, 'assets', 'img')
DEBUG = '--debug' in sys.argv        # adds data-o="<original selector>" hooks for the measuring script

data = json.load(open(os.path.join(HERE, 'home-data.json'), encoding='utf-8'))
manifest = {unquote(m['url']): m['file'] for m in json.load(open(os.path.join(RESEARCH, 'data', 'assets-manifest.json'), encoding='utf-8'))}
for m in json.load(open(os.path.join(RESEARCH, 'data', 'images.json'), encoding='utf-8')):
    manifest.setdefault(unquote(m['src']), m['local'])
CDN = 'https://cdn.prod.website-files.com/662900dde231ae49b618dda8/'

def local(url):
    return os.path.join(RESEARCH, manifest[unquote(url)])

def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')

def copy(url, name):
    """Copy a small asset unchanged. Returns (relative path, width, height)."""
    dst = os.path.join(IMG, name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copyfile(local(url), dst)
    if name.endswith('.svg'):
        s = open(dst, encoding='utf-8').read(600)
        w, h = re.search(r'width="([\d.]+)', s), re.search(r'height="([\d.]+)', s)
        size = (int(float(w.group(1))), int(float(h.group(1)))) if w and h else (0, 0)
    else:
        size = Image.open(dst).size
    return 'assets/img/' + name, size[0], size[1]

def webp(url, name, max_w=None, max_h=None, q=82):
    """Re-save a large photo as WebP, never upscaling. Returns (relative path, width, height)."""
    dst = os.path.join(IMG, name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        im = Image.open(local(url))
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        w, h = im.size
        k = min((max_w or w) / w, (max_h or h) / h, 1)
        if k < 1:
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=q, method=6)
    w, h = Image.open(dst).size
    return 'assets/img/' + name, w, h

def o(key):
    return f' data-o="{key}"' if DEBUG else ''

def img(src, w, h, cls, alt='', lazy=False, key=None):
    # lazy is only safe where the stylesheet fixes the box (slider covers, backdrop). Images sized by
    # their own file would take no room until loaded and make the page grow under the visitor.
    extra = ' loading="lazy" decoding="async"' if lazy else ''
    return f'<img class="{cls}" src="{src}" width="{w}" height="{h}" alt="{escape(alt)}"{extra}{o(key) if key else ""}>'

# ---------------------------------------------------------------- assets
ui = {
    'logo': copy(data['misc']['logo'], 'logo.avif'),
    'hero': copy(data['misc']['hero'], 'hero.avif'),
    'arrow': copy(data['misc']['arrow'], 'icons/arrow-down.svg'),
    'chevron': copy(data['misc']['chevron'], 'icons/chevron-right.svg'),
    'stars': copy(data['misc']['stars'], 'icons/stars.svg'),
    'about_bg': copy(data['misc']['about_bg'], 'about-bg.avif'),
    'card_bg': copy(data['service_bg'], 'card-bg.avif'),
}
copy(CDN + '68791f69b96dea907465a877_left-arrow.avif', 'icons/slider-prev.avif')
copy(CDN + '687918e0f803033a043c0f4f_right-arrow.png', 'icons/slider-next.png')

# Favicon and fonts were captured into the earlier wireframe folder, not site-research.
WIREFRAME = os.path.join(os.path.dirname(OUT), 'wireframe', 'assets')
for src, dst in [('img/662900dee231ae49b618de46_3222.png', 'img/favicon.png'),
                 ('img/662900dee231ae49b618de47_circle.png', 'img/apple-touch-icon.png'),
                 ('fonts/KFO7CnqEu92Fr1ME7kSn66aGLdTylUAMa3yUBA.woff2', 'fonts/roboto-latin.woff2'),
                 ('fonts/KFO7CnqEu92Fr1ME7kSn66aGLdTylUAMa3KUBGEe.woff2', 'fonts/roboto-latin-ext.woff2')]:
    os.makedirs(os.path.dirname(os.path.join(OUT, 'assets', dst)), exist_ok=True)
    if not os.path.exists(os.path.join(OUT, 'assets', dst)):
        shutil.copyfile(os.path.join(WIREFRAME, src), os.path.join(OUT, 'assets', dst))

# Client logos: file name, alt text. The number is the size class the original gives each logo.
BRAND_NAMES = ['accuhealth', 'bevager', 'luxe-places', 'zultys', 'jc-undertaking', 'market-hero',
               'happy-diab', 'client-8', 'client-9', 'client-10', 'ice', 'lorenzon']
BRAND_ALT = ['Accuhealth', 'Bevager', 'Luxe Places', 'Zultys', 'JC Undertaking', 'Market Hero',
             'Happy Diab', '', '', '', 'ICE', 'Lorenzon']
brands = []
for b, name, alt in zip(data['brands'], BRAND_NAMES, BRAND_ALT):
    ext = os.path.splitext(unquote(b['src']))[1]
    brands.append((copy(b['src'], f'brands/{name}{ext}'), b['n'], alt))

COUNTERS = [('15', 'Industries transformed', 'industries'), ('50', 'Startups launched', 'startups'), ('10,000', 'Active users across our clients', 'users')]
counter_icons = [copy(u, f'icons/stat-{n[2]}.svg') for u, n in zip(data['counter_icons'], COUNTERS)]
service_icons = [copy(s['icon'], f'icons/service-{i + 1}.svg') for i, s in enumerate(data['services'])]
process_icons = [copy(s['icon'], f'icons/process-{i + 1}.svg') for i, s in enumerate(data['process'])]
# Team changes made after the capture (the live site still shows the old list).
TEAM_REMOVED = {'Sabina A'}
# New members. The photo is a ready-made file in assets/img/team/: 865 x 817 with the same
# blue-to-purple background as the others.
TEAM_ADDED = [
    {'name': 'Mos R.', 'role': 'FullStack & Automation Engineer', 'photo': 'team/mostafizur-rahman.webp'},
]
# Order on the page: left to right, row by row, two per row (on phones: top to bottom).
#   Artur A    | Dmitry K
#   Kristina D | Tony B
#   Dmytro Z   | Mosh H
#   Dmitry S   | Mos R.
TEAM_ORDER = ['Artur A', 'Dmitry K', 'Kristina D', 'Tony B', 'Dmytro Z', 'Mosh H', 'Dmitry S', 'Mos R.']
members = {}
for t in data['team']:
    if t['name'] not in TEAM_REMOVED:
        members[t['name']] = (webp(t['img'], f"team/{slug(t['name'])}.webp", q=88), t)
for t in TEAM_ADDED:
    w, h = Image.open(os.path.join(IMG, t['photo'])).size
    members[t['name']] = (('assets/img/' + t['photo'], w, h), t)
assert set(members) == set(TEAM_ORDER) and len(TEAM_ORDER) == len(members), 'TEAM_ORDER must list every team member once'
team = [members[name] for name in TEAM_ORDER]
shown = {os.path.basename(f[0]) for f, _ in team}
for name in os.listdir(os.path.join(IMG, 'team')):      # drop photos of people who are no longer shown
    if name not in shown:
        os.remove(os.path.join(IMG, 'team', name))
platforms = [(copy(p['img'], f'{n}.avif'), p['href'], alt) for p, n, alt in zip(data['platforms'], ['fiverr-pro', 'upwork-expert-vetted'], ['Fiverr Pro', 'Upwork Expert-Vetted'])]
projects = [(webp(p['img'], f"projects/{p['href'].rsplit('/', 1)[1]}.webp", max_w=800, q=86), p) for p in data['projects']]
POSTS_ON_HOME = 12      # the live site lists 100 here (Webflow's default limit); newest first
posts = [(webp(p['img'], f"blog/{p['href'].rsplit('/', 1)[1]}.webp", max_w=832, q=82), p) for p in data['posts'][:POSTS_ON_HOME]]
used = {os.path.basename(f[0]) for f, _ in posts}
for name in os.listdir(os.path.join(IMG, 'blog')):      # drop covers of posts that are no longer shown
    if name not in used:
        os.remove(os.path.join(IMG, 'blog', name))

# ---------------------------------------------------------------- repeating blocks
def brand_group(hidden):
    items = ''.join(
        f'\n            <li class="brands__item">{img(f[0], f[1], f[2], f"brands__logo brands__logo--{n}", "" if hidden else alt)}</li>'
        for f, n, alt in brands)
    return f'\n          <ul class="brands__group"{" aria-hidden=" + chr(34) + "true" + chr(34) if hidden else o("div.brands-loop_box")}>{items}\n          </ul>'

def stat(i):
    num, label, _ = COUNTERS[i]
    f = counter_icons[i]
    k = i == 0
    return f'''
          <div class="stat"{o("div.counter-item_box") if k else ""}>
            {img(f[0], f[1], f[2], "stat__icon", key="img.icon-section_counter" if k else None)}
            <div class="stat__text"{o("div.counter-text_box") if k else ""}>
              <p class="stat__value"{o("div.titlel-item_counter") if k else ""}><span{o("div.counter-text_big.counternumbers") if k else ""}>{num}</span><span>+</span></p>
              <p class="stat__label"{o("div.counter-text_description") if k else ""}>{label}</p>
            </div>
          </div>'''

def service(i, s):
    f = service_icons[i]
    k = i == 0
    return f'''
          <li class="dot-card service"{o("div.content-item_services") if k else ""}>
            {img(f[0], f[1], f[2], "service__icon", key="img.icon-service" if k else None)}
            <h3 class="service__title"{o("div.heading-text_service") if k else ""}>{escape(s["title"])}</h3>
            <p class="service__text"{o("div.description-card-service") if k else ""}>{escape(s["text"])}</p>
          </li>'''

def card(f, p, i, kind):
    k = i == 0 and kind == 'project'
    tag = ''
    if 'cat' in p:
        tag = f'''
                <p class="card__meta"{o("div.category-content_wrapper.mg-bottom-12px") if k else ""}><span class="card__tag"{o("div.category-item_projects") if k else ""}>{escape(p["cat"])}</span><span class="card__time"{o("div.text_time") if k else ""}>{escape(p["time"])}</span></p>'''
    return f'''
            <li class="slider__slide"{o("div.swiper-slide.basic-swiperr-item.w-dyn-item.swiper-slide-active") if k else ""}>
              <a class="card" href="{escape(p["href"])}"{o("a.projects_content-wrapper.w-inline-block") if k else ""}>
                {img(f[0], f[1], f[2], "card__image", lazy=i > 3, key="img.image_projects" if k else None)}{tag}
                <h3 class="card__title"{o("h3.title-text_projects") if k else ""}>{escape(p["title"])}</h3>
                <p class="card__text"{o("div.description-text_projects") if k else ""}>{escape(p["text"])}</p>
                <span class="card__more"{o("div.button-collection_projects") if k else ""}><span class="card__more-label">Read more</span><span class="card__more-icon">{img(ui["chevron"][0], 24, 24, "card__chevron", lazy=i > 3)}</span></span>
              </a>
            </li>'''

def member(f, t, i):
    k = i == 0
    return f'''
          <li class="member"{o("div.team-item-wrap") if k else ""}>
            <div class="member__avatar">{img(f[0], f[1], f[2], "member__photo", key="img.member-avatar" if k else None)}</div>
            <div class="member__info"{o("div.member-info-wrap") if k else ""}>
              <h3 class="member__name"{o("h3.member-name") if k else ""}>{escape(t["name"])}</h3>
              <p class="member__role"{o("div.member-role") if k else ""}>{escape(t["role"])}</p>
            </div>
          </li>'''

def step(i, s):
    f = process_icons[i]
    k = i == 0
    size = {'size-short': ' step__text--short', 'size-l': ' step__text--long'}.get(s['size'], '')
    return f'''
          <li class="dot-card step"{o("div.content-item_process") if k else ""}>
            {img(f[0], f[1], f[2], "step__icon", key="img.icon-process" if k else None)}
            <h3 class="step__title"{o("div.heading-text_process") if k else ""}>{escape(s["title"])}</h3>
            <p class="step__text{size}"{o("div.description-card-process") if k else ""}>{escape(s["text"])}</p>
          </li>'''

def review(i, r):
    k = i == 0
    return f'''
            <li class="slider__slide review-slide"{o("div.swiper-slide.auto-height-item.w-dyn-item.swiper-slide-active") if k else ""}>
              <figure class="review"{o("div.auto-height_content") if k else ""}>
                <figcaption class="review__head"{o("div.mg-bottom-24px.swiper") if k else ""}>
                  <div class="review__author"{o("div.wrapper_clients-info") if k else ""}>
                    <p class="review__name"{o("div.client-name_text") if k else ""}>{escape(r["name"])}</p>
                    <p class="review__role"{o("div.client-position_text") if k else ""}>{escape(r["role"])}</p>
                  </div>
                  {img(ui["stars"][0], 116, 19, "review__stars", "Rated 5 out of 5", key="img.icon_stars" if k else None)}
                </figcaption>
                <blockquote class="review__text"{o("div.reviews_text") if k else ""}>{escape(r["text"])}</blockquote>
              </figure>
            </li>'''

NL = '\n'
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Artech Digital</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="assets/img/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="stylesheet" href="css/styles.css">
  <script src="js/main.js" defer></script>
</head>
<body>

  <header class="site-header"{o("div.header.w-nav")}>
    <div class="site-header__bar"{o("div.container-main.is-header")}>
      <a class="site-header__brand" href="/" aria-label="Artech Digital, home"{o("a.w-nav-brand.w--current")}>
        {img(ui["logo"][0], ui["logo"][1], ui["logo"][2], "site-header__logo", key="img.image_brand")}
      </a>
      <nav class="site-nav" id="site-nav" aria-label="Main"{o("nav.nav-menu.w-nav-menu")}>
        <div class="site-nav__panel"{o("div.navmenu_content")}>
          <a class="site-nav__link" href="#Services"{o("a.header_nav-link.w-inline-block")}>Services</a>
          <a class="site-nav__link" href="#Projects">Projects</a>
          <a class="site-nav__link" href="#Reviews">Reviews</a>
          <a class="site-nav__link" href="#About-us">About Us</a>
          <a class="site-nav__link" href="/blog">Blog</a>
          <a class="button button--outline" href="#Contact"{o("a.button-main.is-header.w-inline-block")}>Contact</a>
        </div>
      </nav>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav"{o("div.menu-button.menu_button.w-nav-button")}>Menu</button>
    </div>
  </header>

  <main>
    <div class="intro"{o("div.overflow-wrapper")}>

      <section class="hero" id="AI-Solutions"{o("section.section_hero")}>
        <div class="hero__inner"{o("div.container-main.hero")}>
          <div class="hero__copy"{o("div.column-wrapper.is-hero-static")}>
            <h1 class="hero__title"{o("h1.h1-hero")}>From Business Problem to Production-Ready AI</h1>
            <p class="hero__lead"{o("div.subtitle-text_hero")}>We design and build AI-powered products, agents, and automation systems that increase revenue, reduce manual work, and turn your expertise into scalable software.</p>
            <div class="hero__actions"{o("div.align-left.mobile-flex-vertical")}>
              <a class="button" href="#Contact"{o("a.button-main.w-inline-block")}>Book an AI Strategy Call</a>
            </div>
          </div>
          <div class="hero__media"{o("div.column-wrapper.is-hero-img")}>
            {img(ui["hero"][0], ui["hero"][1], ui["hero"][2], "hero__image", key="img.image-big_hero")}
          </div>
        </div>
        <div class="hero__scroll"{o("div.arrow-item_absolute")}>
          <a class="circle-link" href="#Benefits" aria-label="Scroll to the next section"{o("a.arrow-item_hero.w-inline-block")}>{img(ui["arrow"][0], ui["arrow"][1], ui["arrow"][2], "circle-link__icon")}</a>
        </div>
        <div class="hero__backdrop" aria-hidden="true">
          <span class="glow glow--hero-1"></span>
          <span class="glow glow--hero-2"></span>
          <span class="glow glow--hero-3"></span>
          <span class="glow glow--hero-4"></span>
          <span class="glow glow--hero-5"></span>
          <span class="rule rule--hero"><span class="rule__line"></span></span>
        </div>
      </section>

      <section class="stats" id="Benefits"{o("section.section_counter")}>
        <div class="stats__panel"{o("div.wrapper-content_counter")}>{stat(0)}
          <span class="stats__divider"{o("div.divider-item_counter")}></span>{stat(1)}
          <span class="stats__divider"></span>{stat(2)}
        </div>
        <div class="brands">
          <p class="brands__title"{o("div.subtitle-color_text.bold")}>Trusted by founders and businesses:</p>
          <div class="brands__viewport"{o("div.brands-loop_wrapper")}>
            <div class="brands__track">{brand_group(False)}{brand_group(True)}{brand_group(True)}
            </div>
          </div>
        </div>
        <span class="rule rule--stats" aria-hidden="true"><span class="rule__line"></span></span>
      </section>

    </div>

    <section class="services" id="Services"{o("section.section_services")}>
      <div class="services__inner"{o("div.container-main.is-relative")}>
        <header class="section-heading section-heading--raised"{o("div.heading-content_box.mg-down-48px.is-relative")}>
          <h2 class="section-heading__title section-heading__title--compact"{o("h2.title-section_services")}>WHAT WE BUILD</h2>
          <p class="section-heading__sub"{o("div.subtitle-color_text.is-orange")}>AI THAT SOLVES REAL BUSINESS PROBLEMS</p>
        </header>
        <ul class="services__grid"{o("div.inner-container.is-services")}>{"".join(service(i, s) for i, s in enumerate(data["services"]))}
        </ul>
        <div class="services__backdrop" aria-hidden="true">
          <span class="glow glow--services-1"></span>
          <span class="glow glow--services-2"></span>
          <span class="glow glow--services-3"></span>
        </div>
      </div>
    </section>

    <section class="showcase showcase--projects" id="Projects"{o("section.section_projects")}>
      <div class="showcase__inner" data-slider="cards"{o("div.container-main.projects")}>
        <header class="section-heading"{o("div.heading-content_box.mg-down-48px")}>
          <h2 class="section-heading__title"{o("h2.title-section_projects")}>Projects</h2>
          <p class="section-heading__sub">Explore our case studies</p>
        </header>
        <div class="slider" data-slider-viewport>
          <ul class="slider__track" data-slider-track{o("div.swiper-wrapper.basic-slider-list.w-dyn-items")}>{"".join(card(f, p, i, "project") for i, (f, p) in enumerate(projects))}
          </ul>
        </div>
        <div class="slider-nav"{o("div.swiper-arrow-wrapper")}>
          <button class="round-button round-button--prev round-button--solid" type="button" data-slider-prev aria-label="Previous projects"{o("div.slider-button-left.is-project.swiper-button-disabled")}></button>
          <button class="round-button round-button--next round-button--solid" type="button" data-slider-next aria-label="Next projects"{o("div.slider-button-right.is-project")}></button>
        </div>
      </div>
    </section>

    <section class="team"{o("section.section_team")}>
      <div class="team__inner">
        <header class="section-heading"{o("div.heading-content_box.mg-bottom-m")}>
          <h2 class="section-heading__title">Meet the Product Team</h2>
        </header>
        <ul class="team__grid"{o("div.collection-list-team.w-dyn-items")}>{"".join(member(f, t, i) for i, (f, t) in enumerate(team))}
        </ul>
      </div>
      <div class="team__backdrop" aria-hidden="true"><span class="glow glow--team"></span></div>
    </section>

    <section class="process"{o("section.section_process")}>
      <div class="process__inner">
        <header class="section-heading section-heading--raised">
          <h2 class="section-heading__title">Our Proven Process for Success</h2>
          <p class="section-heading__sub section-heading__sub--strong">FROM BUSINESS PROBLEM TO PRODUCTION</p>
        </header>
        <ol class="process__steps"{o("div.process-content-wrap")}>{"".join(step(i, s) for i, s in enumerate(data["process"]))}
        </ol>
        <div class="process__actions"{o("div.button-wrap_process")}>
          <a class="button" href="#Contact">Reach out to learn more</a>
        </div>
        <div class="process__backdrop" aria-hidden="true">
          <span class="glow glow--process-1"></span>
          <span class="glow glow--process-2"></span>
          <span class="glow glow--process-3"></span>
        </div>
      </div>
    </section>

    <section class="contact" id="Contact"{o("section.section_call")}>
      <div class="contact__inner"{o("div.container-main.is-call")}>
        <div class="contact__intro"{o("div.column-wrapper.is-call")}>
          <h2 class="contact__title"{o("h2.title-section_call")}>Schedule a call today to see if we are the right partner</h2>
          <a class="button" href="#booking">Book a Call</a>
        </div>
        <div class="contact__widget"{o("div.column-wrapper.widget")}>
          <div class="contact__calendar" id="booking" data-calendly="https://calendly.com/artech-digital/website-intro-call?hide_event_type_details=1&amp;hide_gdpr_banner=1"{o("div.calendly-inline-widget")}></div>
        </div>
        <span class="rule rule--contact" aria-hidden="true"><span class="rule__line"></span></span>
      </div>
    </section>

    <section class="about" id="About-us"{o("section.section_benefits")}>
      <div class="about__inner"{o("div.limiter-width_benefits")}>
        <h2 class="about__title"{o("h2.title-section_benefits")}>5-Star Results, Real-World Impact</h2>
        <p class="about__text"{o("div.text-content_benefits")}>With <strong>120+ verified 5-star reviews</strong> across Upwork and Fiverr, we rank in the <strong>Top 1% of Upwork&#x27;s Expert-Vetted talent</strong> and hold <strong>Top Rated Seller</strong> and <strong>Fiverr Pro</strong> status in AI, Data Science, and Software Development.<br><br>Founders and business owners - from early-stage startups to established companies — work with us because we consistently:<br>- Ship production-ready products on time and on budget<br>- Maintain a <strong>96%+ Job Success Score</strong> with a track record of repeat clients<br>- Pair senior engineering with clear, jargon-free communication<br><br>When you partner with us, you&#x27;re not gambling on a freelancer. You&#x27;re tapping into an agency whose reputation is built one successful launch at a time.</p>
        <div class="about__badges"{o("div.wrapper-platform_logos")}>{"".join(f"""
          <a class="about__badge" href="{href}"{o("a.link_platform.w-inline-block") if n == 0 else ""}>{img(f[0], f[1], f[2], "about__badge-image", alt, key="img.icon_benefits" if n == 0 else None)}</a>""" for n, (f, href, alt) in enumerate(platforms))}
        </div>
      </div>
      <div class="about__backdrop" aria-hidden="true">
        {img(ui["about_bg"][0], ui["about_bg"][1], ui["about_bg"][2], "about__backdrop-image", lazy=True)}
      </div>
    </section>

    <section class="reviews" id="Reviews"{o("section.section_reviews")}>
      <div class="reviews__inner">
        <h2 class="reviews__title"{o("h2.title-section_reviews")}>What People Say About Us:</h2>
        <div class="reviews__slider" data-slider="reviews"{o("div.reviews_slider-wrapper")}>
          <div class="slider slider--reviews" data-slider-viewport>
            <ul class="slider__track" data-slider-track{o("div.swiper-wrapper.auto-height-list.w-dyn-items")}>{"".join(review(i, r) for i, r in enumerate(data["reviews"]))}
            </ul>
          </div>
          <div class="slider-nav slider-nav--reviews"{o("div.auto-height-buttons-wrapper")}>
            <button class="round-button round-button--prev" type="button" data-slider-prev aria-label="Previous reviews"></button>
            <button class="round-button round-button--next" type="button" data-slider-next aria-label="Next reviews"></button>
          </div>
        </div>
      </div>
      <div class="reviews__backdrop" aria-hidden="true"><span class="glow glow--reviews"></span></div>
    </section>

    <section class="showcase showcase--blog" id="Blog"{o("section.section_blog.overflow-wrapper")}>
      <div class="showcase__inner" data-slider="cards">
        <header class="section-heading section-heading--blog"{o("div.heading-content_box.mg-bottom-60px")}>
          <h2 class="section-heading__title">Our Latest Posts</h2>
        </header>
        <div class="slider" data-slider-viewport>
          <ul class="slider__track" data-slider-track>{"".join(card(f, p, i, "post") for i, (f, p) in enumerate(posts))}
          </ul>
        </div>
        <div class="slider-nav">
          <button class="round-button round-button--prev round-button--solid" type="button" data-slider-prev aria-label="Previous posts"></button>
          <button class="round-button round-button--next round-button--solid" type="button" data-slider-next aria-label="Next posts"></button>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer"{o("section.section_footer")}>
    <div class="site-footer__main">
      <div class="site-footer__columns"{o("div.container-main.footer")}>
        <div class="site-footer__about"{o("div.content-column_footer")}>
          <div class="site-footer__brand"><a class="site-footer__brand-link" href="/" aria-label="Artech Digital, home"{o("a.brand-logo.w-inline-block")}>{img(ui["logo"][0], ui["logo"][1], ui["logo"][2], "site-footer__logo", key="img.footer_logo")}</a></div>
          <p class="site-footer__line site-footer__tagline"{o("a.subscribe_link.w-inline-block")}>Artech Digital — Your Technical Partner From Idea to Launch</p>
          <p class="site-footer__line"><a class="site-footer__email" href="mailto:artur@artech-digital.com">artur@artech-digital.com</a></p>
          <address class="site-footer__line">2900 W Anderson Lane<br>Ste C 200 PMB 1063<br>Austin, TX 78757<br>United States</address>
        </div>
        <div class="site-footer__subscribe"{o("div.content-column_footer.right")}>
          <p class="site-footer__label site-footer__label--strong"{o("div.footer_text.weight-medium")}>Subscribe</p>
          <p class="site-footer__label site-footer__label--intro">Stay Connected with Us</p>
          <form class="subscribe" data-subscribe{o("div.footer_form-block.w-form")}>
            <div class="subscribe__row"{o("div.form-box_footer")}>
              <input class="subscribe__field" type="email" name="email" maxlength="256" placeholder="Your Email Here" aria-label="Email address"{o("input.text-field_footer.w-input")}>
              <input class="subscribe__submit" type="submit" value="Join"{o("input.sumbit-button_footer.w-button")}>
            </div>
            <p class="subscribe__message" role="status" hidden>Thank you! Your submission has been received!</p>
          </form>
          <p class="site-footer__note"{o("div.additional-text_footer")}>By subscribing, you agree to our <a class="site-footer__note-link" href="/privacy"{o("a.additional-link_privacy")}>Privacy Policy</a>.</p>
        </div>
      </div>
      <div class="site-footer__top"{o("div.wrapper-arrow_footer")}>
        <a class="circle-link circle-link--up" href="#AI-Solutions" aria-label="Back to top"{o("a.arrow-item_footer.w-inline-block")}>{img(ui["arrow"][0], ui["arrow"][1], ui["arrow"][2], "circle-link__icon")}</a>
      </div>
    </div>
    <div class="site-footer__bar">
      <div class="site-footer__legal"{o("div.container-main.footer.is-bottom")}>
        <p class="site-footer__copyright"{o("div.mobile-item_view")}>© 2026 Artech Digital. All rights reserved.</p>
        <a class="site-footer__legal-link" href="/privacy"{o("a.page-link_footer")}>Privacy Policy</a>
      </div>
    </div>
  </footer>

</body>
</html>
'''

open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
total = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(os.path.join(OUT, 'assets')) for f in fs)
print(f'index.html {len(html) // 1024} KB, assets {total / 1e6:.1f} MB, debug hooks: {DEBUG}')
