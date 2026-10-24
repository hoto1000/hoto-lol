# hoto.lol

Static blog + podcast site. No framework, no trackers.

- Edit posts in `content/posts/`, list them in `POSTS` in `build.py`.
- Add episodes: drop audio in `podcasts/`, add to `EPISODES` in `build.py`.
- Build: `python3 build.py` (writes `public/`). Commit `public/` too.
- Deploys on Cloudflare Workers (static assets) via `wrangler.jsonc`. No build command needed.
