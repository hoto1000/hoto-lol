#!/usr/bin/env python3
"""Builds the Project Hoto site (hoto.lol) into ./docs. Run: python3 build.py

To add a blog post: write the body HTML in content/posts/<slug>.html,
then add an entry to POSTS below (newest first).
To add an episode: put the audio in podcasts/ and add an entry to EPISODES.
"""
import html
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "Project Hoto"

POSTS = [
    {
        "slug": "a-school-should-be-a-harbor",
        "title": "A school should be a harbor, not a sorting machine",
        "date": "2026-10-24",
        "summary": "Eight small, testable ways to make a school feel safe: private help, a calm start, a quiet room, meals without shame, and rules that listen.",
    },
    {
        "slug": "how-great-thinkers-are-made",
        "title": "How great thinkers are made",
        "date": "2026-10-23",
        "summary": "Six habits that build a sharper mind, from reading the originals to arguing with people who disagree.",
    },
]

EPISODES = [
    {
        "slug": "a-study-on-happiness",
        "title": "A Study on Happiness",
        "date": "2026-10-23",
        "length": "9 min",
        "summary": "What happiness really is, why change matters, and why learning every side of politics can help us know ourselves.",
        "audio": "/podcasts/why-modern-happiness-is-broken.m4a",
        "overview": [
            "Hi, and welcome to a study on happiness. I believe happiness is worth studying as carefully as we study anything else, because it shapes every part of how we live.",
            "We often think happiness means feeling joyful all the time. But real happiness is quieter than that. It's contentment. It's being at peace with your own life, even when that life is hard. Every generation in history has faced turmoil, loss, and struggle. The people who found happiness didn't escape those things. They learned to carry them.",
            "I believe God built change into the world. Change can feel frightening, but it's also how we grow. Maybe change is part of a larger design, one meant to protect us and move us toward something better.",
            "If happiness can be studied, then so can the society around us. I'll be honest. I don't know where I stand on politics yet. But I know I don't want to be apolitical. I believe every ideology has its strengths and its blind spots. And if more of us took the time to really understand them, I think we'd gain something powerful: self-awareness, and a clearer sense of who we are.",
            "That's what this country is supposed to be about. Freedom. The freedom to be whoever we want to be. So I want to ask hard questions, like whether the Constitution should be updated to reflect who we are today. Over the past century, America has become far more diverse. Maybe our founding rules should grow with the people they serve.",
            "So let's ask the big questions together. What makes a life feel full? And how can we build a country where more people get to feel that way?",
        ],
    },
]

NAV = [("/", "Home"), ("/blog/", "Blog"), ("/podcasts/", "Podcasts"), ("/civic/", "Civic guide")]

PLAYER_JS = """<script>
document.querySelectorAll('.player button').forEach(function (b) {
  b.addEventListener('click', function () {
    var a = document.createElement('audio');
    a.controls = true; a.preload = 'none'; a.src = b.dataset.src;
    a.setAttribute('aria-label', b.dataset.title);
    b.replaceWith(a); a.play().catch(function () {});
  });
});
</script>"""


def esc(s):
    return html.escape(s, quote=True)


def page(path, title, description, body, script=""):
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if (href == path or (href != "/" and path.startswith(href))) else ""}>{label}</a>'
        for href, label in NAV
    )
    full_title = SITE if title is None else f"{title} · {SITE}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-adsense-account" content="ca-pub-2462240112532447">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2462240112532447" crossorigin="anonymous"></script>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="crisis" role="note">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</div>
<header class="top">
<a class="wordmark" href="/">Project <span>Hoto</span></a>
<nav class="main" aria-label="Main">{nav}</nav>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<p>Essays, episodes, and questions worth sitting with.</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p>Ads help keep this site free. They are served by Google, which may use cookies. <a href="/privacy/">Privacy</a>.</p>
</footer>
{script}
</body>
</html>
"""


def write(rel, text):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


def post_list(posts):
    items = "".join(
        f'<li><time datetime="{p["date"]}">{p["date"]}</time><br>'
        f'<a class="title" href="/blog/{p["slug"]}/">{esc(p["title"])}</a>'
        f'<p>{esc(p["summary"])}</p></li>'
        for p in posts
    )
    return f'<ul class="list">{items}</ul>'


def episode_card(e, full=True):
    overview = ""
    if full:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    return f"""<section class="episode" id="{e['slug']}" aria-labelledby="{e['slug']}-h">
<p class="meta"><time datetime="{e['date']}">{e['date']}</time> · {e['length']}</p>
<h3 id="{e['slug']}-h">{esc(e['title'])}</h3>
<p>{esc(e['summary'])}</p>
<div class="player"><button type="button" data-src="{e['audio']}" data-title="{esc(e['title'])}">▶ Play episode</button></div>
{overview}
</section>"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "site.css", OUT / "site.css")
    shutil.copy(ROOT / "favicon.svg", OUT / "favicon.svg")
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    (OUT / "CNAME").write_text("hoto.lol\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "ads.txt").write_text("google.com, pub-2462240112532447, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text("User-agent: Mediapartners-Google\nAllow: /\n\nUser-agent: *\nDisallow: /\n")

    # Home
    latest = EPISODES[0]
    write("index.html", page("/", None, "Plain-spoken essays and podcast episodes on happiness, schools, thinking, and civic life.", f"""
<p class="kicker">Essays · Episodes · Questions</p>
<h1>Big questions, asked plainly.</h1>
<p class="lede">Short essays and podcast episodes about happiness, schools, how to think, and how we live together.</p>
<h2>Latest writing</h2>
{post_list(POSTS[:3])}
<p><a class="back" href="/blog/">All posts →</a></p>
<h2>Latest episode</h2>
{episode_card(latest, full=False)}
<p><a class="back" href="/podcasts/">All episodes →</a></p>
<h2>Planet Hoto</h2>
<p>Plain-language mental health help for the practical side of life: finding care, paying for it, work, housing, and asking for help. <a href="/blog/">Read the blog →</a></p>
<h2>Civic guide: where do my political views sit?</h2>
<p>A neutral, privacy-first self-reflection tool. Seven policy areas, each on its own line, no labels and no voting advice. Your answers never leave your device, and the guide has no ads. <a href="/civic/">Try the civic guide →</a></p>
""", PLAYER_JS))

    # Blog index
    write("blog/index.html", page("/blog/", "Blog", "Plain-spoken essays. Education and opinion only.", f"""
<h1>Blog</h1>
<div class="note"><p><strong>Heads up: these posts are blunt.</strong> That is a style choice, not a judgment of you.</p>
<p>If a post stirs up something heavy, you can stop reading any time.</p></div>
{post_list(POSTS)}
"""))

    # Posts
    for p in POSTS:
        body = (ROOT / "content" / "posts" / f"{p['slug']}.html").read_text(encoding="utf-8")
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], f"""
<article>
<a class="back" href="/blog/">← Back to the blog</a>
<h1>{esc(p['title'])}</h1>
<p><time datetime="{p['date']}">{p['date']}</time></p>
{body}
<p><a class="back" href="/blog/">← Back to the blog</a></p>
</article>
"""))

    # Podcasts
    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcasts", "Podcast episodes, starting with a study on happiness.", f"""
<h1>Podcasts</h1>
<div class="note"><p>These episodes are personal reflections and opinions. They are conversation, not therapy.</p>
<p>Nothing plays until you press Play.</p></div>
{cards}
""", PLAYER_JS))

    # Civic guide: a standalone page, deliberately NOT built with page(), so it never
    # loads the AdSense script. Its own CSP blocks all network requests. Political and
    # social-location answers must never reach ads, analytics, or storage.
    quiz = (ROOT / "civic" / "quiz.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in quiz and "adsbygoogle" not in quiz, "civic guide must not load ads"
    assert "connect-src 'none'" in quiz, "civic guide must keep its no-network CSP"
    write("civic/index.html", quiz)

    # Privacy
    write("privacy/index.html", page("/privacy/", "Privacy", "How this site handles your data and ads.", """
<h1>Privacy</h1>
<p>No accounts. No forms. Nothing you type here is sent to this site.</p>
<h2>Ads</h2>
<p>This site shows ads from Google AdSense. Google and its partners may use cookies to show ads based on your visits to this and other sites.</p>
<p>You can turn off personalized ads at <a href="https://adssettings.google.com/" rel="noopener noreferrer">Google Ad Settings</a>, and learn more at <a href="https://policies.google.com/technologies/ads" rel="noopener noreferrer">how Google uses data in ads</a>.</p>
<h2>Civic guide</h2>
<p>The <a href="/civic/">civic guide</a> has no ads, trackers, or analytics. It blocks all network requests, so your answers cannot be sent anywhere. Answers are kept only in the open page, never saved to your browser, and disappear when you leave or press “Reset all answers.” Your political answers are never used for ads, accounts, or retargeting.</p>
<h2>Podcast audio</h2>
<p>Episodes are hosted on this site and only load when you press Play.</p>
"""))

    # 404
    write("404.html", page("/404", "Not found", "Page not found.", """
<h1>Nothing here.</h1>
<p>That page does not exist. <a href="/">Go home</a>.</p>
"""))


if __name__ == "__main__":
    build()
    print("Built", sum(1 for _ in OUT.rglob("*.html")), "pages into", OUT)
