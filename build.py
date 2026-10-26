#!/usr/bin/env python3
"""Builds the Project Hoto site (hoto.lol) into ./docs. Run: python3 build.py

To add a blog post: write the body HTML in content/posts/<slug>.html,
then add an entry to POSTS below (newest first). Each entry needs a type
("opinion", "explainer" or "essay") and a theme (one of THEMES); "disclaimer"
is optional. Reading time is computed from the post body at build time.
To add an episode: put the audio in podcasts/ and add an entry to EPISODES.
"""
import html
import math
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "Project Hoto"

POSTS = [
    {
        "slug": "a-president-who-understands-how-systems-feel",
        "title": "A President Who Understands How Systems Feel",
        "date": "2026-10-25",
        "type": "opinion",
        "theme": "Politics and civic life",
        "disclaimer": "Personal opinion; not affiliated with her or any campaign.",
        "summary": "Why I might support Alexandria Ocasio-Cortez if she runs for president in 2028: social location, her record, and a politics that connects housing, health, climate, and daily costs.",
    },
    {
        "slug": "when-watching-students-becomes-the-lesson",
        "title": "When Watching Students Becomes the Lesson",
        "date": "2026-10-24",
        "type": "essay",
        "theme": "Schools",
        "summary": "Schools collect more data on students than ever. They should have to show it helps, explain it, and let people push back when it is wrong.",
    },
    {
        "slug": "a-school-should-be-a-harbor",
        "title": "A school should be a harbor, not a sorting machine",
        "date": "2026-10-24",
        "type": "essay",
        "theme": "Schools",
        "summary": "Eight small, testable ways to make a school feel safe: private help, a calm start, a quiet room, meals without shame, and rules that listen.",
    },
    {
        "slug": "a-most-agreeable-war",
        "title": "A Most Agreeable War",
        "date": "2026-10-23",
        "type": "essay",
        "theme": "Politics and civic life",
        "summary": "An essay in the manner of an old drawing-room novel: on the pride of the men who start wars and the prejudice of the people asked to cheer them on.",
    },
    {
        "slug": "what-im-learning-about-third-parties",
        "title": "What I'm Learning About Third Parties",
        "date": "2026-10-23",
        "type": "explainer",
        "theme": "Politics and civic life",
        "summary": "Most Americans say they want a third major party and almost none vote for one. A sourced explainer on why third parties lose, what they win anyway, and the reforms already changing the rules.",
    },
    {
        "slug": "a-rest-from-happiness",
        "title": "A Rest From Happiness",
        "date": "2026-10-23",
        "type": "essay",
        "theme": "Mind and how to live",
        "summary": "Being happy is good. Being expected to be happy all the time is work, and work needs breaks. On giving yourself permission to just be okay.",
    },
    {
        "slug": "how-great-thinkers-are-made",
        "title": "How great thinkers are made",
        "date": "2026-10-23",
        "type": "essay",
        "theme": "Mind and how to live",
        "summary": "Six habits that build a sharper mind, from reading the originals to arguing with people who disagree.",
    },
]

EPISODES = [
    {
        "slug": "is-toxic-happiness-making-us-miserable",
        "title": "Is Toxic Happiness Making Us Miserable?",
        "date": "2026-10-24",
        "length": "7 min",
        "summary": "Is the pressure to always be happy making us miserable? An audio episode.",
        "audio": "/podcasts/is-toxic-happiness-making-us-miserable.m4a",
        "overview": [],
    },
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

THEMES = [
    ("politics", "Politics and civic life"),
    ("schools", "Schools"),
    ("mind", "Mind and how to live"),
]
THEME_ID = {name: tid for tid, name in THEMES}

TYPE_LABELS = {"opinion": "Opinion", "explainer": "Sourced explainer", "essay": "Essay"}

NAV = [("/blog/#start", "Start here"), ("/blog/", "Essays"), ("/podcasts/", "Podcasts"), ("/civic/", "Civic guide")]

TAGLINE = "Ask the hard questions. Argue them fairly."
CRISIS_TEXT = "In crisis? Call or text 988 (U.S.) or call 911 for an emergency."
FOOTER_LINES = [
    "Independent and unofficial. Not affiliated with AOC or any campaign.",
    "Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.",
    "This site currently shows no ads.",
]
BLUNT = "That is a style choice, not a judgment of you."


def esc(s):
    return html.escape(s, quote=True)


def current_nav(path):
    """The nav href that matches this page, or None. Start here is never current."""
    if path == "/" or path.startswith("/blog/"):
        return "/blog/"
    for href in ("/podcasts/", "/civic/"):
        if path.startswith(href):
            return href
    return None


def header_html(path):
    cur = current_nav(path)
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if href == cur else "", label)
        for href, label in NAV
    )
    return (
        '<header class="site-head"><div class="shell">\n'
        '<a class="wordmark" href="/blog/">Project <span class="mk">Hoto</span></a>\n'
        f'<nav class="main-nav" aria-label="Main">{nav}</nav>\n'
        "</div></header>"
    )


def footer_html():
    links = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    return (
        '<footer class="site-foot"><div class="shell">\n'
        f'<p class="tagline">{TAGLINE}</p>\n'
        f'<nav aria-label="Footer">{links}</nav>\n'
        f"<p>{FOOTER_LINES[0]}</p>\n"
        f"<p>{FOOTER_LINES[1]}</p>\n"
        f'<p>{FOOTER_LINES[2]} <a href="/privacy/">Privacy</a>.</p>\n'
        "</div></footer>"
    )


def page(path, title, description, body, script=""):
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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
{header_html(path)}
<main id="main" tabindex="-1">
{body}
</main>
{footer_html()}
{script}
</body>
</html>
"""


def write(rel, text):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def nice(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m) - 1]} {int(dd)}, {y}"


def reading_min(body):
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return max(1, math.ceil(len(text.split()) / 230))


def load_body(p):
    body = (ROOT / "content" / "posts" / f"{p['slug']}.html").read_text(encoding="utf-8")
    # Generated pages may not contain em dashes. Source posts are left untouched;
    # the dash is rendered as a comma (the pairs in the AOC post read as asides).
    return body.replace("—", ", ")


def prepare_posts():
    for p in POSTS:
        assert p["type"] in TYPE_LABELS, p["slug"]
        assert p["theme"] in THEME_ID, p["slug"]
        p["body"] = load_body(p)
        p["reading_min"] = reading_min(p["body"])


def tag(kind):
    label = TYPE_LABELS[kind]
    cls = {"opinion": "tag-opinion", "explainer": "tag-explainer", "essay": "tag-essay"}[kind]
    return f'<span class="tag {cls}">{label}</span>'


def post_card(p, feature=False):
    disc = f'<p class="disclaimer">{esc(p["disclaimer"])}</p>' if p.get("disclaimer") else ""
    cta = '<span class="button button-primary">Read the essay</span>' if feature else ""
    meta = (f'<span class="meta">{tag(p["type"])}<time class="date" datetime="{p["date"]}">{nice(p["date"])}</time>'
            f'<span>{p["reading_min"]} min read</span></span>')
    cls = "entry feature" if feature else "entry"
    return (f'<a class="{cls}" href="/blog/{p["slug"]}/">{meta}'
            f'<h3>{esc(p["title"])}</h3><p class="sum">{esc(p["summary"])}</p>{disc}{cta}</a>')


def front_page():
    ep = EPISODES[0]
    by_slug = {p["slug"]: p for p in POSTS}
    tp = by_slug["what-im-learning-about-third-parties"]
    latest = POSTS[0]

    steps = [
        (f'<span class="meta"><span class="tag tag-tool">Private tool</span></span>'
         '<h3>Where do my political views sit?</h3>'
         '<p class="sum">Seven policy areas, no labels, no voting advice. Your answers never leave your device.</p>',
         "/civic/"),
        (f'<span class="meta">{tag("explainer")}<span>{tp["reading_min"]} min read</span></span>'
         f'<h3>{esc(tp["title"])}</h3>'
         '<p class="sum">Most Americans say they want a third major party and almost none vote for one. Why third parties lose, what they win anyway, and the reforms already changing the rules.</p>',
         f'/blog/{tp["slug"]}/'),
        (f'<span class="meta"><span class="tag tag-podcast">Podcast</span><span>{ep["length"]}</span></span>'
         f'<h3>{esc(ep["title"])}</h3><p class="sum">{esc(ep["summary"])}</p>',
         f'/podcasts/#{ep["slug"]}'),
    ]
    steps_html = "".join(
        f'<li><span class="step-n" aria-hidden="true">{i}</span><a class="entry" href="{href}">{inner}</a></li>'
        for i, (inner, href) in enumerate(steps, 1)
    )

    chips, sections = "", ""
    for tid, name in THEMES:
        posts = [p for p in POSTS if p["theme"] == name]
        if not posts:
            continue
        chips += f'<li><a href="#{tid}">{esc(name)} <sup aria-label="{len(posts)} pieces">{len(posts)}</sup></a></li>'
        cards = "".join(f"<li>{post_card(p)}</li>" for p in posts)
        sections += (f'<section class="theme" id="{tid}" aria-labelledby="{tid}-h"><div class="shell">'
                     f'<div class="sec-head"><h2 class="sec-h" id="{tid}-h">{esc(name)}</h2>'
                     f'<span class="count">{len(posts)} {"piece" if len(posts) == 1 else "pieces"}</span></div>'
                     f'<ul class="cards">{cards}</ul></div></section>')

    return f"""<section class="intro shell">
<div>
<p class="kicker">An independent, personal civic blog</p>
<h1>{TAGLINE}</h1>
<p class="lede">Plain-spoken essays, a podcast, and a private civic self-check on schools, politics, and how we live together. One person's views, with sources, and room for you to disagree.</p>
</div>
<div class="callout"><p><strong>Independent and unofficial.</strong> Project Hoto is a personal project. It is not affiliated with, endorsed by, or paid for by Alexandria Ocasio-Cortez, any campaign, party, or political committee. Essays are opinion. Sourced claims are linked where they appear.</p></div>
</section>

<div class="lead-grid shell">
<section aria-labelledby="latest-h">
<div class="sec-head"><h2 class="sec-h" id="latest-h">Latest</h2></div>
{post_card(latest, feature=True)}
</section>
<section id="start" aria-labelledby="start-h">
<div class="sec-head thin"><h2 class="sec-h" id="start-h">Start here</h2><span class="count">About 30 min</span></div>
<p class="sub">New? Take these three in order.</p>
<ol class="steps" role="list">{steps_html}</ol>
</section>
</div>

<section class="themes shell" aria-labelledby="themes-h">
<h2 class="sec-h" id="themes-h">Browse by theme</h2>
<ul class="chips">{chips}</ul>
<div class="heads-up"><p><strong>Heads up: these posts are blunt.</strong> {BLUNT} If a post stirs up something heavy, you can stop reading any time. Disagree? Good. Read the other side's best case too.</p></div>
</section>
{sections}"""


def end_mark(body):
    """Insert the decorative end mark after the last prose paragraph (before any sources block)."""
    cut = body.find('<section id="sources"')
    head, tail = (body, "") if cut == -1 else (body[:cut], body[cut:])
    i = head.rfind("</p>")
    mark = '\n<div class="end" aria-hidden="true"><span class="end-mark"></span></div>\n'
    if i == -1:
        return head + mark + tail
    i += len("</p>")
    return head[:i] + mark + head[i:] + tail


def essay_page(idx):
    p = POSTS[idx]
    newer = POSTS[idx - 1] if idx > 0 else None
    older = POSTS[idx + 1] if idx + 1 < len(POSTS) else None
    tid = THEME_ID[p["theme"]]

    def nb(q, rel, label):
        if not q:
            return ""
        return (f'<a class="entry" rel="{rel}" href="/blog/{q["slug"]}/"><span class="dir">{label}</span>'
                f'<h3>{esc(q["title"])}</h3></a>')

    links = nb(newer, "next", "Newer") + nb(older, "prev", "Older")
    keep = f'<div class="keep-grid">{links}</div>' if links else ""
    return page(f"/blog/{p['slug']}/", p["title"], p["summary"], f"""
<article class="essay">
<a class="back" href="/blog/">← Back to essays</a>
<p class="meta">{tag(p["type"])}<time datetime="{p['date']}">{nice(p['date'])}</time><span>{p['reading_min']} min read</span><a href="/blog/#{tid}">{esc(p['theme'])}</a></p>
<h1>{esc(p['title'])}</h1>
<p class="dek">{esc(p['summary'])}</p>
<div class="heads-up"><p><strong>Heads up: these posts are blunt.</strong> If a post stirs up something heavy, you can stop reading any time.</p></div>
<div class="body">
{end_mark(p['body'])}
</div>
<section class="keep" aria-labelledby="keep-h">
<h2 id="keep-h">Keep reading</h2>
{keep}
<p class="all"><a class="button button-secondary" href="/blog/">All essays</a></p>
</section>
</article>
""")


def episode_card(e):
    overview = ""
    if e["overview"]:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    return f"""<section class="episode" id="{e['slug']}" aria-labelledby="{e['slug']}-h">
<p class="meta"><span class="stamp">{e['length']}</span><time datetime="{e['date']}">{nice(e['date'])}</time></p>
<h2 id="{e['slug']}-h">{esc(e['title'])}</h2>
<p class="sum">{esc(e['summary'])}</p>
<audio controls preload="none" src="{e['audio']}" aria-label="{esc(e['title'])}"></audio>
{overview}
</section>"""


def build():
    prepare_posts()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "site.css", OUT / "site.css")
    shutil.copy(ROOT / "favicon.svg", OUT / "favicon.svg")
    shutil.copytree(ROOT / "fonts", OUT / "fonts")
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    (OUT / "CNAME").write_text("hoto.lol\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "ads.txt").write_text("google.com, pub-2462240112532447, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text("User-agent: Mediapartners-Google\nAllow: /\n\nUser-agent: *\nDisallow: /\n")

    # Front page: the same page at /blog/ and /index.html (hoto.lol/ redirects to /blog/ at the CDN,
    # and old pages still link to /index.html).
    desc = "An independent, personal civic blog: plain-spoken essays, a podcast, and a private civic self-check."
    write("blog/index.html", page("/blog/", None, desc, front_page()))
    write("index.html", page("/", None, desc, front_page()))

    for i, p in enumerate(POSTS):
        write(f"blog/{p['slug']}/index.html", essay_page(i))

    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcasts", "Podcast episodes, starting with a study on happiness.", f"""
<div class="page-head shell">
<h1>Podcasts</h1>
<div class="heads-up"><p>These episodes are personal reflections and opinions. They are conversation, not therapy.</p>
<p>Nothing plays until you press Play.</p></div>
</div>
<div class="episodes shell">
{cards}
</div>
"""))

    # Civic guide: a standalone page, deliberately NOT built with page(), so it never
    # loads the AdSense script. Its own CSP blocks all network requests. Political and
    # social-location answers must never reach ads, analytics, or storage.
    # Its header and footer are literal markup in quiz.html; they must match the shared ones.
    quiz = (ROOT / "civic" / "quiz.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in quiz and "adsbygoogle" not in quiz, "civic guide must not load ads"
    assert "connect-src 'none'" in quiz, "civic guide must keep its no-network CSP"
    assert header_html("/civic/") in quiz, "civic/quiz.html header is out of sync with header_html()"
    assert footer_html() in quiz, "civic/quiz.html footer is out of sync with footer_html()"
    write("civic/index.html", quiz)

    write("privacy/index.html", page("/privacy/", "Privacy", "How this site handles your data and ads.", """
<div class="plain-page">
<h1>Privacy</h1>
<p>No accounts. No forms. Nothing you type here is sent to this site.</p>
<h2>Ads</h2>
<p>This site does not currently show ads. If that changes, this page will be updated before any ads appear.</p>
<h2>Civic guide</h2>
<p>The <a href="/civic/">civic guide</a> has no ads, trackers, or analytics. It blocks all network requests, so your answers cannot be sent anywhere. Answers are kept only in the open page, never saved to your browser, and disappear when you leave or press “Reset all answers.” Your political answers are never used for ads, accounts, or retargeting.</p>
<h2>Podcast audio</h2>
<p>Episodes are hosted on this site and only load when you press Play.</p>
</div>
"""))

    write("404.html", page("/404", "Not found", "Page not found.", """
<div class="plain-page">
<h1>Nothing here.</h1>
<p>That page does not exist. <a href="/blog/">Go home</a>.</p>
</div>
"""))


def visible_text(doc):
    doc = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", doc)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", doc)).split())


def verify():
    """Fail the build on anything the site promises never to ship."""
    errors = []
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT)
        doc = f.read_text(encoding="utf-8")
        if "—" in doc:
            errors.append(f"{rel}: contains an em dash")
        for m in re.finditer(r"(?is)<(link|script|img)\b[^>]*>", doc):
            if re.search(r"""(?i)\b(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", m.group(0)):
                errors.append(f"{rel}: external request in {m.group(0)[:80]}")
        text = visible_text(doc)
        if CRISIS_TEXT not in text or 'href="tel:988"' not in doc or 'href="tel:911"' not in doc:
            errors.append(f"{rel}: crisis strip missing or changed")
        for line in FOOTER_LINES:
            if line not in text:
                errors.append(f"{rel}: footer line missing: {line[:40]}")
        if '<a href="/privacy/">Privacy</a>' not in doc:
            errors.append(f"{rel}: footer Privacy link missing")
        for m in re.finditer(r"\[[^\]\n]{1,30}\]", text):
            errors.append(f"{rel}: bracketed placeholder text {m.group(0)!r}")
    size = sum(f.stat().st_size for f in (ROOT / "fonts").rglob("*") if f.is_file())
    if size > 120 * 1024:
        errors.append(f"fonts/ is {size} bytes (limit 122880)")
    if errors:
        print("Build checks failed:", *errors, sep="\n  ", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()
    verify()
    print("Built", sum(1 for _ in OUT.rglob("*.html")), "pages into", OUT)
