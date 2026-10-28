# Margin step 4: accessibility and responsive audit

Scope: `/`, `/blog/`, long post (`what-arendt-meant-by-the-banality-of-evil`), short post (`a-president-who-understands-how-systems-feel`), `/podcasts/`, `/civic/`, `/how-i-argue/`, `/privacy/`, `404.html`.
Method: headless Chromium (Playwright 1.63) against `docs/` served at the site root, axe-core (latest from npm) with tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa and best-practice, at 320, 390, 768 and 1280 px wide, with `prefers-color-scheme` light and dark. That is 9 pages x 4 widths x 2 themes = 72 runs, before and after the fixes. Scripts were kept outside the repo (no dependency added to the repo).

## Results after the fixes

"All 8" means 4 widths x 2 themes.

| Check | home | blog | long post | short post | podcasts | civic | how-i-argue | privacy | 404 |
|---|---|---|---|---|---|---|---|---|---|
| axe, 0 violations (A/AA/2.1/2.2 + best-practice) | pass all 8 | pass all 8 | pass all 8 | pass all 8 | pass all 8 | pass all 8 (see note 1) | pass all 8 | pass all 8 | pass all 8 |
| No horizontal scroll (320, 390, 768, 1280; also 640 = 200% of 1280) | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| 320x256 viewport (= 400% zoom of 1280x1024), no clipped or overlapping text, details opened | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| Exactly one h1, one main, one banner, one contentinfo | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| Heading levels do not skip | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| Visible navs have distinct names (Main, The argument, Read next, Footer) | pass | pass | pass | pass | pass | pass (no footer nav, own footer) | pass | pass | pass |
| Skip link first, then crisis links, then wordmark and Menu or nav, then main, then footer | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| Skip link target `#main` exists and takes focus | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| Focus ring present, 3 px, at least 3:1 against its background, not clipped (390 and 1280, both themes) | pass | pass | pass (fixed, defect 2) | pass | pass | pass | pass | pass | pass |
| Reduced motion: no animation, transition or smooth scroll | pass | pass | pass | pass | pass | pass (note 2) | pass | pass | pass |

Other checks:

| Check | Result |
|---|---|
| Phone Menu (`details.menu`) opens and closes with Enter and Space; Tab moves into its links | pass |
| Post TOC (`details.toc-phone`) opens and closes with Enter and Space; Tab moves into its links | pass |
| Print: Menu, nav, TOC and skip link hidden, black on white, crisis strip kept | pass (emulated print, light and dark) |
| Post bodies (`div.prose`) byte-identical to main, all 14 posts | pass |

Token contrast (computed, WCAG relative luminance):

| Pair | Light | Dark |
|---|---|---|
| text on canvas / surface | 14.15 / 12.36 | 15.51 / 12.39 |
| muted on canvas / surface | 6.29 / 5.49 | 9.65 / 7.71 |
| link on canvas / surface | 7.61 / 6.65 | 10.87 / 8.68 |
| focus ring on canvas / surface | 14.15 / 12.36 | 15.51 / 12.39 |
| accent on canvas / surface | 4.19 / 3.66 | 8.57 / 6.84 |

The light accent is used only for the wordmark (24 px bold, large text, needs 3:1), the current-page underline and 3 px left rules (non-text, needs 3:1). It is never used for small text. Type-label badges use the text color. Separator borders (`--border`, 1.58:1 light) are decorative and not needed to identify anything; the Menu button and the TOC summary are identified by their text and icon, so 1.4.11 does not require 3:1 on their outline.

## Defects found and fixed

1. **Civic guide lost its colors (serious, found by looking, not by axe).** `civic/quiz.html` defines `--text: var(--ink)`, `--surface: var(--card)`, `--accent: var(--ink)`, and `site.css` defined `--ink: var(--text)`, `--card: var(--surface)`, `--mark: var(--accent)`. These custom properties referenced each other in a cycle, so they all became invalid. Result on main: the "Start" button was transparent with page-colored text and border (invisible), the cards had no background or border, and the strip text colors fell back. axe only reported the Start button as "incomplete" (1:1). Fixed in `site.css` only: the legacy names (`--paper --card --ink --ink-2 --hair --mark`) now hold literal values for light and dark, so nothing cycles. `civic/quiz.html` is untouched. Verified visually in both themes.
2. **Post outline sidebar clipped the focus ring (WCAG 2.4.7/2.4.11).** `.toc-wide` scrolls (`overflow-y: auto`), which cut off the 3 px ring plus 3 px offset on every link. Fixed with 6 px of inner padding and a matching negative margin; the accent rule is drawn with a background gradient so it keeps its exact width.
3. **No print rule.** Added a minimal `@media print`: black on white, hides skip link, Menu, desktop nav, both TOCs and the blog subject sidebar. The crisis strip is kept.

No other defect was found in: contrast, target size, reflow, zoom, reduced motion, landmarks, headings, or tab order.

## Target size

Every link, button and summary is at least 24x24. The primary controls (crisis links, wordmark, Menu, nav links, row links, TOC links, back link, footer links, doors, about links, 404 button) are all at least 44 px tall at every width tested. Two source links in the long post's Sources list ("Stanford Encyclopedia of Philosophy", "United States Holocaust Memorial Museum") are 18 px tall at 768 and wider. They are in post body text, which must not change, and they pass WCAG 2.5.8 through the spacing exception (at least 12 px clear of any other target). Left as is.

## CSS removed (confirmed unused in `build.py`, generated `docs/` and `civic/quiz.html`)

- `.hl, .qm { background: none; color: inherit; padding: 0 }`: a no-op reset. The markup still emitted `<span class="hl">` (home h1) and `<span class="qm">` (closing `?` of questions and the 404 h1). I removed the empty spans from `build.py` too, so no page uses the class. Rendered text is unchanged.
- `.toc-phone li + li a { border-top: 0 }`: dead, those links have no border.
- Custom properties nothing reads: `--fs-post-h1` (two definitions), `--s8`, `--mark-ink`, `--rule`, `--serif`.
- No leftover `q-*` or outline rules exist: `.q-text` is still used by Read next, and the two `outline` rules are the focus ring and the podcast `:target` ring.
- Every remaining class selector in `site.css` is present in the built pages, `build.py` or the quiz.

## Left open, and not tested

1. `civic/quiz.html` (do-not-touch): after "Start", the quiz steps have no h1 (axe `page-has-heading-one`, a best-practice rule, not WCAG A/AA). WCAG axe tags show 0 violations in all states I clicked through (Before you start, Economic policy, Public services, Civil liberties). Results and later steps were not exhaustively tested. The quiz also has its own header and nav (no Menu, no footer nav), so the "Menu or nav" tab order differs there. Needs a decision before touching that file.
2. The quiz's slider transition is already guarded by `prefers-reduced-motion: no-preference`.
3. The 404 button and civic "Start" button report 1.0:1 focus-ring contrast in my script, because the ring is the same color as the filled button. The ring sits 3 px outside the button, against the page canvas (14:1 and 15:1). Not a defect.
4. Audio controls: Chromium draws the focus ring on the `audio` element (checked by screenshot). Other browsers' native audio controls were not tested.
5. Not tested: a real screen reader (NVDA, JAWS, VoiceOver, TalkBack), Safari and Firefox, real devices, browser text-only zoom, forced-colors mode, text-spacing overrides (1.4.12), and actual paper or PDF output (print was checked with emulated print media only). axe cannot judge reading order, link purpose, or whether alt/labels make sense, so those were checked only by structure.
