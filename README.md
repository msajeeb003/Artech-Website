# Artech Digital — home page replica

A hand-written copy of the home page of https://www.artech-digital.com/, built on 26 Nov 2026 from the capture in `../site-research`. Plain HTML, CSS and JavaScript: no Webflow, jQuery, Swiper or any other library.

It was first built to match the live site as closely as possible. Eight faults of the live site were then fixed on request (see "Fixed on purpose" below), so the page now differs from the live site in those places.

## How to open it

- Quickest: double-click `index.html`.
- Better (so links that start with `/` behave like on a real server): open a terminal in this folder, run `python -m http.server 8000`, then visit http://localhost:8000.

Nothing needs to be installed or built.

## What is in the folder

| Path | What it is |
|---|---|
| `index.html` | The page: header, 10 sections, footer |
| `css/styles.css` | All styles. Design tokens are at the top (section 1) |
| `js/main.js` | Menu, the three sliders, Calendly loader, subscribe form |
| `assets/img/`, `assets/fonts/` | 1.6 MB of images and the Roboto font (the live home page loads about 180 MB) |
| `_tools/` | Optional. The scripts that generated the repeating blocks and measured the result. Not needed to run the page |
| `vercel.json`, `.vercelignore` | Settings for deploying to Vercel (see below) |

## Deploying to Vercel

The page is static, so Vercel needs no build step. From a terminal in this folder:

```
npx vercel          # first time: log in and answer the questions; gives a preview address
npx vercel --prod   # publish it as the project's main address
```

Or import the GitHub repository (https://github.com/msajeeb003/Artech-Website) in Vercel. The site sits at the top of the repository, so leave the project's Root Directory empty and the framework on "Other".

What `vercel.json` does:

- **No build**: the files are served as they are. `_tools` and this README are left out of the upload (`.vercelignore`).
- **Links to pages that are not built yet** (`/blog`, `/blog/...`, `/projects/...`, `/privacy`) are sent to the live site, www.artech-digital.com, so they do not end in "page not found". These are temporary redirects. Remove a redirect when you add that page to this folder, otherwise the redirect still wins.
- **Search engines are told not to index** any address other than artech-digital.com, so a `*.vercel.app` copy does not compete with the live site.
- Both rules above switch themselves off on artech-digital.com and www.artech-digital.com. **Do not point the real domain at this project until the blog, case-study and privacy pages exist here**: on the real domain those links would have nowhere to go.
- **Caching**: fonts for a year, images for a day. The page, stylesheet and script are checked for changes on every visit, so edits show at once.
- **Safety headers**: other sites cannot embed the page in a frame, and browsers may not guess file types.

## Reference material used, and what was missing

Used: full-page screenshots at 1920, 1440, 1280, 992, 768 and 390 px; per-section and per-element screenshots; hover and menu-open screenshots; the measured position and size of every element at 1440 and 390 px; the site's fonts, logos, icons and images; the captured text.

Missing, so not reproduced or only approximated:

- The inside of the Calendly booking widget (it belongs to Calendly).
- What the subscribe form does after "Join" (nothing was submitted during the capture).
- Element-by-element measurements of the footer at 1440 px (it was compared by screenshot instead).
- Hover screenshots exist for desktop only.
- Pages other than the home page. Only the home page is built here.

No font had to be substituted: the site uses Roboto, which is free, and the same font files are served from `assets/fonts/`.

## Design tokens

All in `:root` at the top of `css/styles.css`.

- Colours: background `#000211`, text white, button gradient `#2061a8` → `#282c6c`, orange `#f4bd30`, green `#76cd44`, lime `#bcf34d`, link blue `#6ea8e7`, glow `#3138a8`, glass panels white at 10% with a 30% white border.
- Type: Roboto 300 / 400 / 500 / 700, and 900 for the counters. Sizes from 0.75rem to 2.8rem, line heights 1.1 to 1.58.
- Shape: radius 0.25rem (small button), 0.5rem (images), 0.5625rem (main button), 1.94rem and 2rem (panels), full circle.
- Layout: content width 75rem (72.25rem for the sliders), side padding 1.5rem (1rem on phones).

## Screen sizes

Every size is in rem and the root font size follows the screen width, as on the live site.

| Screen width | Layout | Root font size |
|---|---|---|
| 1560px and up | Desktop | 17.33px, fixed |
| 1260–1559px | Desktop, scales like a picture | 14–17.3px (16px at 1440) |
| 992–1259px | Desktop, text stays at 14px, margins and columns narrow | 14px |
| 768–991px | Tablet: "Menu" button, stacked hero, two service columns, two reviews per view | 14px |
| 480–767px | Phone layout, wider cards; two columns for services and team from 600px | 18px |
| up to 479px | Phone layout | about 16.6px at 390, never more than 18px |

The rows from 1260px up and the phone row match the live site. The rows from 480 to 1259px are new (see fix 7).

## How close it is to the live site

Measured with the same screenshot method as the capture (headless Chromium).

**Before the fixes**, the page matched the live site like this:

| Width | Page height, original → replica | Pixels matching |
|---|---|---|
| 1920 | 10004 → 10004 | 99.7% |
| 1440 | 9313 → 9313 | 99.7% |
| 1280 | 8373 → 8373 | 99.7% |
| 992 | 6696 → 6696 | 99.7% |
| 768 | 5375 → 5375 | 99.5% |
| 390 | 11213 → 11213 | 99.0% |

All 11 section heights matched at all six widths, and about 100 elements at 1440 and at 390 matched in position and size to within 0.02px.

**After the fixes:**

- At 1920, 1440, 1280 and 390 the page still matches the live site section by section (1440: every section from Services to Reviews at 99.96–100%). The exceptions are the fixed items: heavier counter numbers, a shorter "Our Latest Posts" section (20–26px, because the 12 remaining cards are less tall than the tallest of 100), and the phone footer line.
- At 992 and 768 the page no longer matches the live site, on purpose: that is the tablet fix.

Checked by script after the fixes: no sideways scrolling at any tested width; menu opens and closes (button, link, outside click, Escape); in-page links land on their section; sliders step by the same distance as the original, stop at the end, follow a mouse drag; the reviews area resizes to the tallest visible review; the subscribe message appears.

Checked by eye only: hover states, and the new layouts at 480, 600, 768, 834, 900, 991, 992, 1024, 1100 and 1259px.

**Re-measured against the live site itself** (fresh screenshots of both, taken on 26 Nov 2026 after the fixes, with the moving logo row frozen in both):

| Width | All sections | Hero (`#AI-Solutions`) |
|---|---|---|
| 1440 | 99.95% | 100.00% |
| 390 | 98.49% | 98.63% |
| 390, replica given the font file Google serves to phones | 99.63% | 100.00% |
| 768 | not comparable: new tablet layout (fix 7) | |

Pixel differences that are not one of the listed fixes:

1. **Phone text edges.** Google Fonts gives phones a different build of Roboto than desktops. The live site therefore uses another font file on phones, while the replica ships the desktop file to everyone. Letter shapes differ by a fraction of a pixel; position and size are identical. This is the whole 98.6% → 100% gap in the phone hero.
2. Photos were re-saved as WebP, which changes fine detail slightly.
3. On the phone layout, two screenshots of the replica are not always identical to each other inside the blurred glass panels (team, process, reviews): some text lines land one pixel higher or lower (99.5% match between two shots). Two screenshots of the live site are identical. I have not found the cause.
4. On the phone layout, the "WHAT WE BUILD" heading and service titles are drawn with a different text-smoothing mode. Position and size are identical. I have not found the cause.
5. The client-logo row moves, so ordinary screenshots never catch it in the same place.

## Every place it differs from the live site

### Fixed on purpose (on request, 26 Nov 2026)

1. **Phone footer** read "© 2024 Company Name. All rights reserved." It now reads "© 2026 Artech Digital. All rights reserved." on every screen size.
2. **Footer links.** The email address is now a mail link (it pointed to `#`). The footer logo goes to the home page. The tagline is plain text (it was a link to nowhere).
3. **Hero down arrow** goes to the next section (it jumped to Contact).
4. **"Book a Call"** scrolls to the booking calendar (it linked to the section it was already in). If you would rather open the Calendly page itself, change its `href` in `index.html`.
5. **Counters** (15+, 50+, 10,000+) now show at weight 900, which the design asked for but the live site never loaded. They look slightly heavier than on the live site.
6. **Logo row on phones** no longer jumps each time it loops.
7. **Tablets and small laptops (480–1259px).** On the live site the whole layout shrinks, so text is 8.5px tall at 768px and about 5px at 480px. Now the text stops shrinking at 14px and the layout adapts, as listed under "Screen sizes". This is new design work, not a copy: please look at it on a tablet.
8. **"Our Latest Posts" shows the 12 newest posts**, not 100. The number is `POSTS_ON_HOME` in `_tools/build.py`. Note: this removes 88 links from the home page to older posts, which may matter for search ranking. The Blog page still lists them.

### Content changed on request

- **Team.** A ninth person is added: **"Mos R., FullStack & Automation Engineer"**. The eight original cards keep their order and places. His card sits last, in the right-hand column under Mosh H; on phones, where the cards are in one column, it is simply last. His photo was prepared to match the others: the background was rebuilt to the same blue-to-purple gradient (the supplied photo had a duller gradient with a dark patch) and it was cropped to the same 865 × 817 shape. The addition is recorded in `TEAM_ADDED` in `_tools/build.py`; the right-column placement of an odd last card is one rule in section 9 of `css/styles.css`.

### Changed for speed, privacy or access

9. **Images re-saved.** Blog and project covers and team photos are WebP. Logos, icons and the hero image are the original files.
10. **Slider cover images load only when needed.** Every other image loads with the page, as on the live site. (An earlier version also delayed the team photos, icons and badges. They take no room until loaded, so the page grew while scrolling and menu links such as "Reviews" stopped up to 550px short. Fixed.)
11. **Roboto is served from this folder**, not from Google Fonts. Rubik is not loaded because no text uses it.
12. **No third-party scripts.** Webflow, jQuery, Swiper, Waypoints, counterUp and typed.js are replaced by about 200 lines in `js/main.js`.
13. **Google Analytics (G-P224QRCRFW) is left out.** Add it back before going live.
14. **Calendly** is a plain embedded frame that loads when the visitor scrolls near it, instead of Calendly's own script at page load. Same booking page, same 800px height.
15. **Subscribe form sends nothing.** After "Join" it shows the original's message ("Thank you! Your submission has been received!") in Webflow's default grey box. That look is an assumption, because the capture never submitted the form. It needs connecting to your mailing-list service.
16. **Slider arrows are real buttons**, so they work with the keyboard. They look the same.
17. **Image descriptions added** for screen readers. Not visible.
18. **The logo row pauses** for visitors whose device asks for reduced motion.

### Rebuilt by hand, so behaviour may differ in detail

19. **Sliders.** Step size, gaps, end stop, drag and review height match. Swiper's drag "feel" (momentum, rubber-band strength) is approximated.
20. **Menu drop-down.** Slides in from the right in 0.4s like the original. At 390px it matches the live site's menu-open screenshot.
21. **Smooth scrolling** for in-page links uses the browser's built-in behaviour, so speed and easing differ slightly from Webflow's.

### Outside this build

22. Links to `/blog`, `/blog/...`, `/projects/...` and `/privacy` point to pages that are not part of this folder.
23. The earlier research notes chose Next.js + Tailwind for the rebuild. This build is plain HTML, CSS and JavaScript, as the brief for this task asked.
24. Only Chromium was measured. The custom scrollbar and the frosted-glass blur depend on the browser, as they do on the live site.

## Re-running the checks (optional)

Needs Python with Pillow, Node with `playwright-core` (`npm install playwright-core`, or set `PLAYWRIGHT_CORE` to the path of an existing copy), and the `site-research` capture folder placed next to this one. The capture is not in this repository (about 1.4 GB).

```
python _tools/extract.py           # captured page -> home-data.json
python _tools/build.py --debug     # index.html with measuring hooks
node _tools/measure.mjs wide-1920 desktop-1440 laptop-1280 mobile-390
node _tools/measure.mjs w768 w992  # any other width: w<pixels>
python _tools/diff.py desktop-1440 mobile-390
node _tools/states.mjs             # menu, sliders, hover, form
python _tools/build.py             # final index.html, no hooks
```
