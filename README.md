# Project Hoto (hoto.lol)

Static blog + podcast site. No framework, no trackers.

- Edit posts in `content/posts/`, list them in `POSTS` in `build.py`.
- Add episodes: drop audio in `podcasts/`, add to `EPISODES` in `build.py`.
- Build: `python3 build.py` (writes `docs/`). Commit `docs/` too.
- Served by GitHub Pages: Settings → Pages → Deploy from branch `main`, folder `/docs`. Custom domain: hoto.lol.

- Civic guide: edit `civic/quiz.html` (standalone page, no ads, no-network CSP). `build.py` copies it to `docs/civic/index.html` and refuses to build if ads are added to it. Review notes: `civic/REVIEW.md`, `civic/PHILOSOPHY-GUIDE.md`.
