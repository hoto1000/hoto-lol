# Project Hoto (hoto.lol)

Static blog + podcast site. No framework, no trackers.

- Edit posts in `content/posts/`, list them in `POSTS` in `build.py`.
- Add episodes: drop audio in `podcasts/`, add to `EPISODES` in `build.py`.
- Build: `python3 build.py` (writes `docs/`). Commit `docs/` too.
- Served by GitHub Pages: Settings → Pages → Deploy from branch `main`, folder `/docs`. Custom domain: hoto.lol.

- Civic guide: edit `civic/quiz.html` (standalone page, no ads, no-network CSP). `build.py` copies it to `docs/civic/index.html` and refuses to build if ads are added to it. Review notes: `civic/REVIEW.md`, `civic/PHILOSOPHY-GUIDE.md`.

## Look and editorial framing (question-journal redesign)

- Every essay is framed by a question. Add or edit that in `FRAMING` in `build.py`, keyed by the post slug: `question`, `theme` (one of `THEMES`), `kind` (Essay, Opinion, Sourced explainer), `sit` (the closing "Sit with this" question), `related` (slug of one "Read next" piece), `voices` (thinkers the piece talks with), and optional `note` and `corrections` (dated fixes shown at the top of the post). `build.py` refuses to build if a slug, theme or related link is wrong.
- Front-page sections live in `DOORS` (Start here), `OPEN_QUESTIONS` (unwritten questions) and `RULES` (How I argue here). The full method page is `/how-i-argue/`.
- Podcast episodes can carry a question in `EPISODE_QUESTIONS`.
- Fonts are self-hosted in `fonts/` (Archivo for headings, Literata for reading), trimmed to Latin and served from this site only. Both are SIL Open Font License; the license texts sit next to the files. No font CDN, no third-party requests.
- Colors and type sizes are CSS variables at the top of `site.css`. Light and dark mode follow the reader's device setting.
- The front page is written to both `/` and `/blog/`, so it works whether or not the home redirect is on.
- The stylesheet link carries a short hash of `site.css` (`/site.css?v=...`, set by `CSS_VERSION` in `build.py`). Cloudflare tells browsers to keep the CSS for 4 hours, so the hash makes a style change show up as soon as the new pages load. Always rebuild after editing `site.css`.
