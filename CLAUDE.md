# Project Hoto (hoto.lol)

Static blog and podcast site. No framework, no trackers, no third-party requests. `build.py` writes the whole site into `docs/`, and GitHub Pages serves `main:/docs` at hoto.lol. Both the source and the built `docs/` are committed.

## Commands

```
python3 build.py              # rebuild docs/ (refuses to build on a bad slug, theme, related link or an ad in the civic guide)
python3 scripts/check_site.py # checks docs/: crisis strip, meta, scripts, headings, ids, links, stylesheet hash, post metadata
```

Run both after every edit, in that order, and commit `docs/` with the source. Standard library only, Python 3.

## Where things live

- Essays: `content/posts/<slug>.html` (body HTML only). Each one is listed in `POSTS` and framed in `FRAMING` in `build.py` (question, theme from `THEMES`, kind, closing "Sit with this" question, one related slug, voices, optional note and dated corrections).
- Podcast: audio in `podcasts/`, listed in `EPISODES`; optional question in `EPISODE_QUESTIONS`.
- Front page: `DOORS` (Start here), `OPEN_QUESTIONS` (unwritten questions), `RULES` (How I argue here), `IDEALS`. The method page is `/how-i-argue/`.
- Civic guide: `civic/quiz.html`, a standalone page with its own CSP and no ads; review notes in `civic/REVIEW.md` and `civic/PHILOSOPHY-GUIDE.md`.
- Look: `site.css` ("Pamphlet 1.1": paper, ink, one yellow highlighter, system serif for reading, self-hosted Archivo Condensed for headings). Colours are CSS variables at the top; light and dark follow the device. The stylesheet link carries a hash of `site.css`, so always rebuild after a CSS change.
- Review notes and past passes: `review/`.

## Hard rules

- Every page keeps the crisis strip (988 and 911 wording in `CRISIS`) and the footer lines. `check_site.py` fails without them.
- No scripts beyond the ones already allowed, no off-site fonts, images or stylesheets, no analytics, no embeds. The civic guide never carries ads.
- One `h1` and one `main` per page, ordered headings, unique ids, working internal links and fragments.
- Essays are the author's own voice and are exempt from the em dash check; everything else the build writes is not.
- Keep "Independent and unofficial" and the "Heads up: these posts are blunt" notices as the build places them.
- No placeholders (`[TODO]`, `[X]`, `[insert ...]`) in built pages; the check fails on them.
- Dates are editorial: a future-dated post is a warning, not a failure, and is left to the author.

## Agents and skills in this repo

- `/new-post <slug or title>`: scaffolds an essay, its `POSTS` and `FRAMING` entries, rebuilds, runs the checks, and reports what the author must still write by hand.
- `site-checker` agent: read-only; rebuilds, runs `check_site.py`, reads the diff and reports findings with file and line.

## Style

Plain, direct sentences. The site frames every essay with a question; new work should fit `THEMES` or propose a theme change explicitly rather than inventing one inline.
