#!/usr/bin/env python3
"""Builds the Project Hoto site (hoto.lol) into ./docs. Run: python3 build.py

To add a blog post: write the body HTML in content/posts/<slug>.html,
then add an entry to POSTS below (newest first).
To add an episode: put the audio in podcasts/ and add an entry to EPISODES.
"""
import datetime
import html
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "Project Hoto"

POSTS = [
    {
        "slug": "a-president-who-understands-how-systems-feel",
        "title": "A President Who Understands How Systems Feel",
        "date": "2026-10-25",
        "summary": "Why I might support Alexandria Ocasio-Cortez if she runs for president in 2028: social location, her record, and a politics that connects housing, health, climate, and daily costs.",
    },
    {
        "slug": "when-watching-students-becomes-the-lesson",
        "title": "When Watching Students Becomes the Lesson",
        "date": "2026-10-24",
        "summary": "Schools collect more data on students than ever. They should have to show it helps, explain it, and let people push back when it is wrong.",
    },
    {
        "slug": "a-school-should-be-a-harbor",
        "title": "A school should be a harbor, not a sorting machine",
        "date": "2026-10-24",
        "summary": "Eight small, testable ways to make a school feel safe: private help, a calm start, a quiet room, meals without shame, and rules that listen.",
    },
    {
        "slug": "a-most-agreeable-war",
        "title": "A Most Agreeable War",
        "date": "2026-10-23",
        "summary": "An essay in the manner of an old drawing-room novel: on the pride of the men who start wars and the prejudice of the people asked to cheer them on.",
    },
    {
        "slug": "what-im-learning-about-third-parties",
        "title": "What I'm Learning About Third Parties",
        "date": "2026-10-23",
        "summary": "Most Americans say they want a third major party and almost none vote for one. A sourced explainer on why third parties lose, what they win anyway, and the reforms already changing the rules.",
    },
    {
        "slug": "a-rest-from-happiness",
        "title": "A Rest From Happiness",
        "date": "2026-10-23",
        "summary": "Being happy is good. Being expected to be happy all the time is work, and work needs breaks. On giving yourself permission to just be okay.",
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

NAV = [("/", "Start here"), ("/blog/", "Essays"), ("/podcasts/", "Podcasts"), ("/civic/", "Civic guide"), ("/about/", "About")]

THEMES = [
    ("Politics and elections", ["a-president-who-understands-how-systems-feel", "what-im-learning-about-third-parties", "a-most-agreeable-war"]),
    ("Schools and education", ["when-watching-students-becomes-the-lesson", "a-school-should-be-a-harbor"]),
    ("Mind and ideas", ["a-rest-from-happiness", "how-great-thinkers-are-made"]),
]

HOW_I_ARGUE = [
    ("Opinion is labeled", "Essays are one person's view, tagged as opinion."),
    ("Claims get sources", "Factual claims link to where they come from."),
    ("Disagreement is welcome", "Challenge the idea, not the person."),
    ("Errors get fixed", "Corrections are noted on the page."),
]

HOME_DESC = "An independent civic blog: essays, podcasts, and a private civic guide. Unofficial, not affiliated with any politician, party, or campaign."
DISCLAIMER = "Independent and unofficial. This site is not affiliated with Alexandria Ocasio-Cortez, any other politician, any party, or any campaign, and nothing here is endorsed by or written for one. When an essay says who the author might support, that is his own opinion."
CIVIC_DESC = "A neutral, privacy-first self-reflection tool. Seven policy areas, each on its own line, no labels and no voting advice. Your answers never leave your device, and the guide has no ads."

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


def nice_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def post_body(p):
    return (ROOT / "content" / "posts" / f"{p['slug']}.html").read_text(encoding="utf-8")


def read_minutes(p):
    words = len(re.sub(r"<[^>]+>", " ", post_body(p)).split())
    return max(1, round(words / 220))


def page(path, title, description, body, script="", og=False):
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
{f'<meta property="og:description" content="{esc(description)}">' + chr(10) if og else ""}<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-adsense-account" content="ca-pub-2462240112532447">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2462240112532447" crossorigin="anonymous"></script>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
<header class="top">
<div class="brand"><a class="wordmark" href="/">Project <span>Hoto</span></a><span class="stamp">Unofficial</span></div>
<nav class="main" aria-label="Main">{nav}</nav>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<p class="foot-brand">Project Hoto</p>
<p>Essays, episodes, and questions worth sitting with.</p>
<p>Independent and unofficial. Not affiliated with any politician, party, campaign, or government.</p>
<ul class="foot-links">
<li><a href="/blog/">Essays</a></li>
<li><a href="/podcasts/">Podcasts</a></li>
<li><a href="/civic/">Civic guide</a></li>
<li><a href="/privacy/">Privacy</a></li>
<li><a href="https://blog.hoto.lol/">Planet Hoto ↗</a></li>
</ul>
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


def post_list(posts, featured=False):
    items = "".join(
        f'<li class="post-card"><p class="meta"><span class="tag">Opinion</span> <time datetime="{p["date"]}">{nice_date(p["date"])}</time> · {read_minutes(p)} min read</p>'
        f'<a class="title" href="/blog/{p["slug"]}/">{esc(p["title"])}</a>'
        f'<p>{esc(p["summary"])}</p><span class="more" aria-hidden="true">Read the essay →</span></li>'
        for p in posts
    )
    # Feature the newest post full width only when the rest pair up evenly.
    cls = "posts featured" if featured and len(posts) >= 3 and len(posts) % 2 == 1 else "posts"
    return f'<ul class="{cls}">{items}</ul>'


def episode_card(e, full=True):
    overview = ""
    if full:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    return f"""<section class="episode" id="{e['slug']}" aria-labelledby="{e['slug']}-h">
<p class="meta"><span class="tag">Audio</span> Episode · <time datetime="{e['date']}">{nice_date(e['date'])}</time> · {e['length']}</p>
<h3 id="{e['slug']}-h">{esc(e['title'])}</h3>
<p>{esc(e['summary'])}</p>
<div class="player"><button type="button" data-src="{e['audio']}" data-title="{esc(e['title'])}">Play episode</button></div>
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
    newest = POSTS[0]
    by_slug = {p["slug"]: p for p in POSTS}
    themes = "".join(
        f'<section class="theme" aria-labelledby="theme-{i}"><h3 id="theme-{i}">{esc(name)}</h3>{post_list([by_slug[x] for x in slugs])}</section>'
        for i, (name, slugs) in enumerate(THEMES)
    )
    argue = "".join(f"<li><h3>{esc(h)}</h3><p>{esc(t)}</p></li>" for h, t in HOW_I_ARGUE)
    write("index.html", page("/", None, HOME_DESC, f"""
<section class="hero" aria-labelledby="hero-h">
<p class="kicker">Essays · Episodes · Questions</p>
<h1 id="hero-h">Big questions, <em>asked plainly.</em></h1>
<p class="lede">Short essays and podcast episodes about happiness, schools, how to think, and how we live together.</p>
<div class="note disclaimer" role="note"><p>{esc(DISCLAIMER)}</p></div>
<div class="actions">
<a class="btn primary" href="/blog/">Read the essays</a>
<a class="btn" href="/podcasts/">Listen to the podcast</a>
</div>
</section>
<section aria-labelledby="start-h">
<div class="section-head"><h2 id="start-h">Start here</h2></div>
<ul class="start">
<li class="start-item"><p class="kicker">Try</p><h3><a href="/civic/">Find where your own views sit</a></h3><p>{esc(CIVIC_DESC)}</p></li>
<li class="start-item"><p class="kicker">Read</p><h3><a href="/blog/{newest['slug']}/">{esc(newest['title'])}</a></h3><p>{esc(newest['summary'])}</p></li>
<li class="start-item"><p class="kicker">Listen</p><h3><a href="/podcasts/#{latest['slug']}">{esc(latest['title'])}</a></h3><p>{esc(latest['summary'])}</p><p class="meta">{latest['length']} · Nothing plays until you press Play.</p></li>
</ul>
</section>
<section aria-labelledby="latest-h">
<div class="section-head"><h2 id="latest-h">Essays by theme</h2><a href="/blog/">All essays →</a></div>
{themes}
</section>
<section aria-labelledby="episode-h">
<div class="section-head"><h2 id="episode-h">Latest episode</h2><a href="/podcasts/">All episodes →</a></div>
{episode_card(latest, full=False)}
</section>
<section aria-labelledby="argue-h">
<div class="section-head"><h2 id="argue-h">How I argue here</h2></div>
<ul class="argue">{argue}</ul>
</section>
<section aria-labelledby="elsewhere-h">
<div class="section-head"><h2 id="elsewhere-h">Also from Hoto</h2></div>
<div class="tiles">
<div class="tile"><p class="kicker">Guides</p><h3><a href="https://blog.hoto.lol/">Planet Hoto ↗</a></h3><p>Plain-language mental health help for the practical side of life: finding care, paying for it, work, housing, and asking for help.</p></div>
<div class="tile"><p class="kicker">Tool</p><h3><a href="/civic/">Civic guide: where do my political views sit?</a></h3><p>{esc(CIVIC_DESC)}</p></div>
</div>
</section>
""", PLAYER_JS, og=True))

    # About
    write("about/index.html", page("/about/", "About", "About this site.", """
<div class="page-head">
<p class="kicker">About</p>
<h1>About</h1>
</div>
<p>[Owner to write: a few sentences on who writes this site and why.]</p>
"""))

    # Blog index
    write("blog/index.html", page("/blog/", "Blog", "Plain-spoken essays. Education and opinion only.", f"""
<div class="page-head">
<p class="kicker">Essays</p>
<h1>Blog</h1>
<p class="lede">Plain-spoken essays. Education and opinion only.</p>
</div>
<div class="note"><p><strong>Heads up: these posts are blunt.</strong> That is a style choice, not a judgment of you.</p>
<p>If a post stirs up something heavy, you can stop reading any time.</p></div>
{post_list(POSTS)}
"""))

    # Posts
    for p in POSTS:
        others = [o for o in POSTS if o["slug"] != p["slug"]][:2]
        more = f"""<section class="keep-reading" aria-labelledby="more-h">
<div class="section-head"><h2 id="more-h">Keep reading</h2><a href="/blog/">All posts →</a></div>
{post_list(others)}
</section>""" if others else ""
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], f"""
<article>
<a class="back" href="/blog/">← Back to the blog</a>
<header>
<p class="kicker">Essay</p>
<h1>{esc(p['title'])}</h1>
<p class="lede">{esc(p['summary'])}</p>
<p class="meta"><time datetime="{p['date']}">{nice_date(p['date'])}</time> · {read_minutes(p)} min read</p>
</header>
<div class="prose">
{post_body(p)}
</div>
<p><a class="back" href="/blog/">← Back to the blog</a></p>
</article>
{more}
"""))

    # Podcasts
    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcasts", "Podcast episodes, starting with a study on happiness.", f"""
<div class="page-head">
<p class="kicker">Audio</p>
<h1>Podcasts</h1>
<p class="lede">Conversations about happiness, change, and how we live.</p>
</div>
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
