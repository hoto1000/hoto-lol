---
name: new-post
description: Scaffold a new hoto.lol essay with its POSTS and FRAMING entries, rebuild, run the checks, and list what the author still writes by hand. Use when the user wants to start a new blog post or essay on hoto.lol.
---

# New post

Arguments: a slug or working title, for example `/new-post why-we-argue-badly`.

1. Read `CLAUDE.md`, then `POSTS`, `THEMES` and `FRAMING` in `build.py`, and one recent post in `content/posts/` as the template for body markup.
2. Agree the frame with the user in one short message: the question the essay answers, the theme (one of `THEMES`), the kind (Essay, Opinion, Sourced explainer), the closing "Sit with this" question, one related slug. Do not invent a new theme.
3. Create `content/posts/<slug>.html` with the heading structure of the template and a short outline in the author's voice. Leave no placeholder brackets; write real sentences or leave the section out.
4. Add the `POSTS` entry (title, date, summary) and the `FRAMING` entry. Dates are the author's call; use today's date unless told otherwise.
5. Run `python3 build.py` then `python3 scripts/check_site.py`. Fix anything that fails in what you added.
6. Delegate to the `site-checker` agent for a read-only pass and address blocking findings.
7. Report: files changed, the check results, and what the author still writes by hand (the essay itself). Do not commit unless asked; when asked, commit source and `docs/` together with a message naming the post.
