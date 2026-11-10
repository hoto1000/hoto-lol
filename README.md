# Project Hoto (hoto.lol)

Static blog + podcast site. No framework, no trackers.

- Edit posts in `content/posts/`, list them in `POSTS` in `build.py`.
- Add episodes: drop audio in `podcasts/`, add to `EPISODES` in `build.py`.
- Build: `python3 build.py` (writes `docs/`). Commit `docs/` too.
- Served by GitHub Pages: Settings → Pages → Deploy from branch `main`, folder `/docs`. Custom domain: hoto.lol.

- Civic guide: edit `civic/quiz.html` (standalone page, no ads, no-network CSP). `build.py` copies it to `docs/civic/index.html` and refuses to build if ads are added to it. Review notes: `civic/REVIEW.md`, `civic/PHILOSOPHY-GUIDE.md`.

## Essay audio

- Every essay gets a Listen player from a file in `audio/`, hosted on this site. Speechify is not used (the build fails if a page mentions it; the old Speechify episodes are listed in `review/speechify-retired.md`).
- Default voice: Kokoro, made offline with `python3 scripts/make_audio.py <slug>` into `audio/<slug>.opus`.
- Nick's ElevenLabs voice: export the narration as MP3 and save it as `audio/<slug>.mp3`. It replaces the Kokoro player for that essay, labeled as an AI clone of Nick's voice. `python3 scripts/make_audio.py <slug> --dry-run` prints the text to paste into ElevenLabs.

## Search engines

- Blog, podcast, method and privacy pages are open to search engines (`index, follow`, a canonical link, and an RSS link to `/feed.xml`).
- The civic guide, voting demo and 404 page stay `noindex` and are never in the sitemap. `robots.txt` allows crawling so search engines can read that `noindex` tag.
- `build.py` writes `docs/sitemap.xml` (every post plus the main pages) and `docs/feed.xml` (RSS of all essays). `check_site.py` checks both.
- Archive and subjects: `/blog/archive/` lists every post by year, and each theme in `THEMES` gets `/topics/<theme>/`. Both are built from `POSTS` and `FRAMING`, so a new post shows up on its own.
- Link previews: every listed page carries Open Graph and social card tags (title, summary, full canonical address) and the share picture `share.png` (1200 x 630, made by `python3 scripts/make_share_image.py`, needs Pillow). Hidden pages get none. `check_site.py` checks them.
- After deploying, submit `https://hoto.lol/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Look and editorial framing (question-journal redesign)

- Every essay is framed by a question. Add or edit that in `FRAMING` in `build.py`, keyed by the post slug: `question`, `theme` (one of `THEMES`), `kind` (Essay, Opinion, Sourced explainer), `sit` (the closing "Sit with this" question), `related` (slug of one "Read next" piece), `voices` (thinkers the piece talks with), and optional `note` and `corrections` (dated fixes shown at the top of the post). `build.py` refuses to build if a slug, theme or related link is wrong.
- Front-page sections live in `DOORS` (Start here) and `RULES` (commitments). The about page, "About this blog", is `/how-i-argue/`.
- Podcast episodes can carry a question in `EPISODE_QUESTIONS`.
- Look: "Pamphlet 1.1". Paper, ink and one yellow highlighter; reading text uses the reader's system serif. Fonts are self-hosted in `fonts/` (Archivo Condensed 800 for headings, labels and buttons), trimmed to Latin and served from this site only. SIL Open Font License; the license text sits next to the file. No font CDN, no third-party requests.
- Colors are CSS variables at the top of `site.css`. Light and dark mode follow the reader's device setting.
- The front page is written to both `/` and `/blog/`, so it works whether or not the home redirect is on.
- The stylesheet link carries a short hash of `site.css` (`/site.css?v=...`, set by `CSS_VERSION` in `build.py`). Cloudflare tells browsers to keep the CSS for 4 hours, so the hash makes a style change show up as soon as the new pages load. Always rebuild after editing `site.css`.

## Checks

After editing anything, rebuild and check:

```
python3 build.py
python3 scripts/check_site.py
```

`build.py` writes `docs/`. `scripts/check_site.py` reads `docs/` (standard library only, no network) and exits non-zero on any failure: crisis strip text, robots/referrer/AdSense meta, scripts and off-site loads, one `h1` and `main` per page, heading levels, unique ids, internal links and fragments, the stylesheet hash, and each post's title, date and summary against `POSTS`. Warnings (for example a future-dated post) are printed but do not fail the run.
