#!/usr/bin/env python3
"""Builds the Project Hoto site (hoto.lol) into ./docs. Run: python3 build.py

To add a blog post: write the body HTML in content/posts/<slug>.html,
then add an entry to POSTS below (newest first).
To add an episode: put the audio in podcasts/ and add an entry to EPISODES.
"""
import hashlib
import html
import math
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "Project Hoto"
# Versioned stylesheet link. Cloudflare tells browsers to keep site.css for 4 hours,
# while pages are kept for 10 minutes. Putting a hash of the CSS in the link means a
# new page always loads the matching styles, and an unchanged stylesheet stays cached.
CSS_VERSION = hashlib.sha256((ROOT / "site.css").read_bytes()).hexdigest()[:10]
CSS_LINK = f'<link rel="stylesheet" href="/site.css?v={CSS_VERSION}">'

POSTS = [
    {
        "slug": "fearless-speech-for-regular-people",
        "title": 'Fearless speech for regular people: parrhesia meets boundary scripts',
        "date": "2026-10-28",
        "summary": "Foucault's idea of parrhesia, what it is not, and four short boundary sentences for work and family.",
    },
    {
        "slug": "you-are-not-the-problem-but-the-label-might-be",
        "title": 'You are not the problem, but the label might be: power/knowledge meets diagnosis',
        "date": "2026-10-27",
        "summary": 'Foucault on power, knowledge and norms: labels can help people, and it is still fair to ask who decided where the line goes.',
    },
    {
        "slug": "the-watcher-in-your-pocket",
        "title": 'The watcher in your pocket: the panopticon meets social media',
        "date": "2026-10-26",
        "summary": 'How a prison design from 1786 explains why we edit ourselves online, and one small thing to try this week.',
    },
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
        "slug": "the-watcher-in-your-pocket-audio",
        "title": 'Why You Police Your Own Behavior',
        "date": "2026-10-28",
        "length": "4 min",
        "summary": 'The panopticon meets social media: why we edit ourselves when we might be watched. Audio version of the essay The Watcher in Your Pocket.',
        "listen_url": "https://speechify.app.link/1ZBUHMzzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "you-are-not-the-problem-audio",
        "title": 'Who Built Your Diagnostic Labels?',
        "date": "2026-10-27",
        "length": "6 min",
        "summary": 'Foucault on power, knowledge and norms. Labels can help, and it is still fair to ask who decided where the line goes. Audio version of the essay.',
        "listen_url": "https://speechify.app.link/Atf111yzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "fearless-speech-audio",
        "title": 'The Courage of Fearless Speech',
        "date": "2026-10-26",
        "length": "4 min",
        "summary": "Foucault's parrhesia, what it is not, and four short boundary sentences. Audio version of the essay.",
        "listen_url": "https://speechify.app.link/2JKZh9xzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "aoc-does-background-dictate-governance",
        "title": "AOC: Does Background Dictate Governance?",
        "date": "2026-10-24",
        "length": "8 min",
        "summary": "A look at how a leader's social location might shape the questions they ask in power, using Alexandria Ocasio-Cortez's possible 2028 run as the example.",
        "listen_url": "https://speechify.app.link/RnX8Xf1Vv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Personal opinion; not affiliated with her or any campaign.",
        "overview": [],
    },
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

# ---------------------------------------------------------------------------
# Editorial framing. Kept separate from POSTS and EPISODES so adding a post or
# an episode stays a one-place edit. Every essay is led by the question it asks.
#   question: the hard question the essay works on (shown above the title)
#   theme:    which shelf it sits on in the question index
#   kind:     Essay, Opinion, or Sourced explainer (opinion is always labeled)
#   sit:      one question for the reader to sit with at the end
#   related:  slug of one essay to read next
#   voices:   thinkers the essay itself names (never add names it doesn't use)
#   corrections: optional list of ("YYYY-MM-DD", "what changed"), shown at the top
# ---------------------------------------------------------------------------
THEMES = ["Politics and elections", "Schools and education", "Mind and ideas"]

FRAMING = {
    "the-watcher-in-your-pocket": {
        "question": 'Do you act differently when you think someone might be watching?',
        "theme": "Mind and ideas",
        "kind": "Sourced explainer",
        "sit": 'Which of your habits would change if nobody could see them?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault', 'Jeremy Bentham'],
    },
    "you-are-not-the-problem-but-the-label-might-be": {
        "question": 'Who decides what counts as normal?',
        "theme": "Mind and ideas",
        "kind": "Sourced explainer",
        "sit": 'Which labels do you carry, and what do they leave out?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault'],
    },
    "fearless-speech-for-regular-people": {
        "question": 'What does it cost you to say the true thing, and is it worth it?',
        "theme": "Mind and ideas",
        "kind": "Sourced explainer",
        "sit": 'What is one sentence you have been rehearsing, and what would it cost to say it?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault'],
    },
    "a-president-who-understands-how-systems-feel": {
        "question": "Can where a leader comes from shape what they see?",
        "theme": "Politics and elections",
        "kind": "Opinion",
        "note": "Personal opinion; not affiliated with her or any campaign.",
        "sit": "Which parts of your own life shape what you notice about how the country works, and what might they hide from you?",
        "related": "what-im-learning-about-third-parties",
        "voices": [],
    },
    "when-watching-students-becomes-the-lesson": {
        "question": "What do students learn when someone is always watching?",
        "theme": "Schools and education",
        "kind": "Essay",
        "sit": "Who should get to decide what counts as a warning sign in a student's life?",
        "related": "a-school-should-be-a-harbor",
        "voices": ["Michel Foucault"],
    },
    "a-school-should-be-a-harbor": {
        "question": "What should school feel like?",
        "theme": "Schools and education",
        "kind": "Essay",
        "sit": "Think of a school you went to. What small thing made you feel wanted, or unwanted, and did anyone in charge know?",
        "related": "when-watching-students-becomes-the-lesson",
        "voices": [],
    },
    "a-most-agreeable-war": {
        "question": "Who starts wars, and who pays for them?",
        "theme": "Politics and elections",
        "kind": "Essay",
        "sit": "When did you last change your mind about people you had judged from far away, and what changed it?",
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ["Jane Austen"],
    },
    "what-im-learning-about-third-parties": {
        "question": "Why do Americans want a third party but almost never vote for one?",
        "theme": "Politics and elections",
        "kind": "Sourced explainer",
        "sit": "If your vote could never be wasted, who would you vote for?",
        "related": "a-president-who-understands-how-systems-feel",
        "voices": ["Maurice Duverger", "Richard Hofstadter"],
    },
    "a-rest-from-happiness": {
        "question": "Is the pressure to be happy making us less happy?",
        "theme": "Mind and ideas",
        "kind": "Essay",
        "sit": "Where in your week are you performing a feeling you don't have, and who is it for?",
        "related": "how-great-thinkers-are-made",
        "voices": ["Arlie Hochschild"],
    },
    "how-great-thinkers-are-made": {
        "question": "How does anyone learn to think well?",
        "theme": "Mind and ideas",
        "kind": "Essay",
        "sit": "What is the one problem you could spend twenty years thinking about?",
        "related": "a-rest-from-happiness",
        "voices": ["Aristotle", "Hobbes", "Madison", "Arendt", "Rawls"],
    },
}

# The question each episode works on, by episode slug (optional).
EPISODE_QUESTIONS = {
    "a-study-on-happiness": "What makes a life feel full?",
}

# Start here: one thing to try, one to read, one to listen to. Read and Listen use the newest POSTS and EPISODES entries.
CIVIC_DESC = ("A neutral, privacy-first self-reflection tool. Seven policy areas, each on its own line, no labels and no voting advice. "
              "Your answers never leave your device, and the guide has no ads.")

# Open questions: topics still being thought through. No essay yet, no deadline.
OPEN_QUESTIONS = [
    ("Who pays the paperwork tax?", "Forms, deadlines and repeat documents make people spend hours just to reach help. Which step could we remove?"),
    ("Can a bus route decide who gets care?", "A service only helps the people who can actually reach it."),
    ("Who gets heard at a public meeting?", "Meeting times, childcare, transit, disability access and language decide who is in the room."),
    ("Is the public library part of the safety net?", "Internet, job searches, a cool room and company, without pretending it can replace housing or health care."),
    ("Who does the hidden second shift?", "School forms, appointments and office hours quietly assume someone has time for unpaid care."),
    ("What does a second chance need?", "One practical barrier after incarceration, like a housing application, without reducing anyone to their record."),
    ("Who shows up after the storm?", "When a tornado or ice storm hits, how much rests on neighbors and local volunteers, and how should everyone else back them up?"),
    ("Can getting help include giving it?", "One Ozarks charity's holiday program has parents pick gifts for their kids and kids pick gifts for their parents, so everyone has something to give. Could public programs protect dignity that way?"),
]

RULES = [
    ("Opinion is labeled.", "When a piece is my view, it says so. Opinion pieces are marked on the index."),
    ("Claims get sources.", "Facts link to where they come from. Uncertain parts are marked as uncertain."),
    ("Disagreement is welcome.", "The strongest fair objection belongs inside the essay, not outside it."),
    ("Errors get fixed.", "If something turns out wrong, I correct it at the top of the post, with the date and what changed."),
]

# Where I start from: ideals borrowed from Heart of the Ozarks (hoto.org), a community
# nonprofit in Springfield, Missouri. Project Hoto is not affiliated with them.
IDEALS = [
    ("Neighbors look after neighbors.", "Storms, layoffs, hunger and family crises hit whole towns at once. I start from the belief that we owe each other help when they do."),
    ("Help now, and a way forward.", "Good help meets the urgent need today and leaves people more able to run their own lives tomorrow. I try to judge policies by both."),
    ("Watch for who falls through the cracks.", "Every rule and program misses someone. I try to name who, and why."),
    ("Everyone has something to give.", "Nobody is only a receiver. A good system leaves room for people to give back, in time, skill or care."),
    ("Start local.", "Big questions land on real streets. Neighbors, local businesses, libraries, faith groups and volunteers are often the first to show up, and I want to learn from them."),
]

IDEALS_CREDIT = ('These ideals borrow from <a href="https://hoto.org/" rel="noopener">Heart of the Ozarks</a>, a community nonprofit '
                 "in Springfield, Missouri, that pairs emergency help with tools for the long run. Project Hoto is not affiliated with them.")

NAV = [("/", "Start here"), ("/blog/", "Essays"), ("/podcasts/", "Podcasts"), ("/civic/", "Civic guide"), ("/about/", "About")]

HOME_DESC = "An independent civic blog: essays, podcasts, and a private civic guide. Unofficial, not affiliated with any politician, party, or campaign."
DISCLAIMER = ("Independent and unofficial. This site is not affiliated with Alexandria Ocasio-Cortez, any other politician, any party, "
              "or any campaign, and nothing here is endorsed by or written for one. When an essay says who the author might support, "
              "that is his own opinion.")

# Home "How I argue here": short versions, exact wording. The full RULES stay on /how-i-argue/.
HOME_RULES = [
    ("Opinion is labeled", "Essays are one person's view, tagged as opinion."),
    ("Claims get sources", "Factual claims link to where they come from."),
    ("Disagreement is welcome", "Challenge the idea, not the person."),
    ("Errors get fixed", "Corrections are noted on the page."),
]

BLUNT = ("<strong>Heads up: these posts are blunt.</strong> That is a style choice, not a judgment of you. "
         "If a post stirs up something heavy, you can stop reading any time.")

UNOFFICIAL = ("<strong>Independent and unofficial.</strong> Project Hoto is a personal project. It is not affiliated with, "
              "endorsed by, or paid for by Alexandria Ocasio-Cortez, any campaign, party, or political committee. "
              "Essays are opinion. Sourced claims are linked where they appear.")


def esc(s):
    return html.escape(s, quote=True)


def q(text):
    """Escape a question and color its closing question mark."""
    t = esc(text)
    if t.endswith("?"):
        return t[:-1] + '<span class="qm">?</span>'
    return t


OPINION_TAG = '<span class="tag">Opinion</span>'
AUDIO_TAG = '<span class="tag">Audio</span>'


def kind_badge(kind):
    """Type label coded by shape as well as words: Opinion is filled, Sourced explainer is boxed, Essay has a square bullet."""
    cls = {"Opinion": "opinion", "Sourced explainer": "sourced"}.get(kind, "essay")
    return f'<span class="kind kind-{cls}">{esc(kind)}</span>'


def page(path, title, description, body, script="", og=False):
    def cur(href):
        on = path == href or (href != "/" and path.startswith(href))
        return ' aria-current="page"' if on else ""

    nav = "".join(f'<a href="{href}"{cur(href)}>{label}</a>' for href, label in NAV)
    foot_nav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    full_title = f"{SITE}: hard questions about how we live together" if title is None else f"{title} · {SITE}"
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
<meta name="theme-color" content="#f2f3f0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#111214" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/archivo-condensed-800.woff2" as="font" type="font/woff2" crossorigin>
{CSS_LINK}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
<header class="top">
<div class="brand"><a class="wordmark" href="/" aria-label="Project Hoto, home">Project <span>Hoto</span></a><span class="stamp">Unofficial</span></div>
<nav class="main" aria-label="Main">{nav}</nav>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<p class="foot-mark">Ask the hard questions. Argue them fairly.</p>
<nav aria-label="Footer">{foot_nav}</nav>
<p>Independent and unofficial. Not affiliated with any politician, party, campaign, or government.</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p>This site currently shows no ads. <a href="/privacy/">Privacy</a>.</p>
</footer>
{script}
</body>
</html>
"""


POST_BODIES = []  # essay bodies as written into pages; they are the author's text and are exempt from the em dash check


def write(rel, text):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def nice(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m) - 1]} {int(dd)}, {y}"


def balance_sections(html):
    """Some post files carry a closing </section> with no opening tag, and leave the
    sources section open. Drop unmatched closers and close anything left open, so the
    page nests cleanly. The post text itself is never changed."""
    out, depth, pos = [], 0, 0
    for m in re.finditer(r"<(/?)section\b[^>]*>", html):
        out.append(html[pos:m.start()])
        if m.group(1):
            if depth:
                depth -= 1
                out.append(m.group(0))
        else:
            depth += 1
            out.append(m.group(0))
        pos = m.end()
    out.append(html[pos:])
    return "".join(out).rstrip() + "\n" + "</section>\n" * depth


def body_of(slug):
    return balance_sections((ROOT / "content" / "posts" / f"{slug}.html").read_text(encoding="utf-8"))


def minutes(slug):
    """Reading time for the essay text, not counting the sources list."""
    text = body_of(slug).split('id="sources"')[0]
    words = len(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
    return max(1, math.ceil(words / 230))


def post(slug):
    return next(p for p in POSTS if p["slug"] == slug)


def frame(slug):
    """Framing for a post. Posts added without framing still build."""
    return {"question": None, "theme": THEMES[-1], "kind": "Essay", "sit": None, "related": None, "voices": [],
            "note": "", "corrections": [], **FRAMING.get(slug, {})}


def question_item(p):
    f = frame(p["slug"])
    headline = q(f["question"]) if f["question"] else esc(p["title"])
    note = f' <em>{esc(f["note"])}</em>' if f["note"] else ""
    title = f'<cite>{esc(p["title"])}</cite> · ' if f["question"] else ""
    return (f'<li><a class="q-link" href="/blog/{p["slug"]}/">'
            f'<h4 class="q-text-wrap"><span class="q-text">{headline}</span></h4>'
            f'<span class="q-meta">{kind_badge(f["kind"])}{"" if f["kind"] == "Opinion" else OPINION_TAG}{title}<time datetime="{p["date"]}">{nice(p["date"])}</time> · {minutes(p["slug"])} min read</span>'
            f'<span class="q-sum">{esc(p["summary"])}{note}</span></a></li>')


def front_page():
    newest, ep = POSTS[0], EPISODES[0]
    start = [
        ("Try", "/civic/", "Find where your own views sit", esc(CIVIC_DESC)),
        ("Read", f'/blog/{newest["slug"]}/', esc(newest["title"]), esc(newest["summary"])),
        ("Listen", f'/podcasts/#{ep["slug"]}', esc(ep["title"]),
         f'{esc(ep["summary"])}<b>{AUDIO_TAG}{esc(ep["length"])} · Nothing autoplays.</b>'),
    ]
    doors = [f'<li class="door"><a href="{href}"><span class="door-label">{label}</span><h3 class="door-q">{name}</h3>'
             f'<span class="door-meta">{text}</span></a></li>' for label, href, name, text in start]

    themes = []
    for t in THEMES:
        items = [p for p in POSTS if frame(p["slug"])["theme"] == t]
        if not items:
            continue
        themes.append(f'<div class="theme"><h3><span class="label">{esc(t)}</span></h3>'
                      f'<ul class="qlist">{"".join(question_item(p) for p in items)}</ul></div>')

    shelf = "".join(f"<li><h3>{q(a)}</h3><p>{esc(b)}</p></li>" for a, b in OPEN_QUESTIONS)
    rules = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in HOME_RULES)
    ideals = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in IDEALS)

    return f"""<div class="frame">
<section class="hero" aria-labelledby="hero-h">
<div class="hero-text">
<p class="kicker">An independent journal of hard questions about society</p>
<h1 id="hero-h">Ask the <span class="hl">hard questions.</span> Argue them fairly.</h1>
<p class="lede">Essays, a podcast and a private civic self-check about power, school and how to live together. One person thinking in public, with sources, and room for you to disagree.</p>
<p class="unofficial notice" role="note">{esc(DISCLAIMER)}</p>
<div class="actions"><a class="cta" href="#start">Start here</a><a class="cta-quiet" href="#questions">See every question</a></div>
</div>
<p class="emblem" aria-hidden="true">?</p>
</section>

<section class="section" id="start" aria-labelledby="start-h">
<div class="section-head"><h2 id="start-h">Start here</h2><p>One to try, one to read, one to hear.</p></div>
<ul class="doors start">{"".join(doors)}</ul>
</section>

<section class="section" id="questions" aria-labelledby="questions-h">
<div class="section-head"><h2 id="questions-h">The questions</h2><p>Every essay starts from one hard question. Newest first in each theme.</p></div>
{"".join(themes)}
<p class="aside-note">{BLUNT}</p>
</section>

<section class="section" id="open" aria-labelledby="open-h">
<div class="section-head"><h2 id="open-h">Open questions</h2><p>Things I am still thinking through. No essay yet, and no deadline.</p></div>
<ul class="shelf">{shelf}</ul>
</section>

<section class="section" id="ideals" aria-labelledby="ideals-h">
<div class="section-head"><h2 id="ideals-h">Where I start from</h2><p>Five ideals behind the questions. When hard times hit, neighbors help each other through.</p></div>
<ul class="rules">{ideals}</ul>
<a class="more" href="/how-i-argue/#ideals">Why these ideals →</a>
</section>

<section class="section" id="how" aria-labelledby="how-h">
<div class="section-head"><h2 id="how-h">How I argue here</h2><p>Rules I hold myself to, so you can see where fact ends and opinion begins.</p></div>
<ul class="rules">{rules}</ul>
<a class="more" href="/how-i-argue/">The full method →</a>
</section>
</div>
"""


def slugify(text):
    t = re.sub(r"<[^>]+>", "", html.unescape(text)).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "part"


def with_outline(body):
    """Give each h2 an id and return (body, outline items). The source files stay untouched."""
    items, seen = [], set(re.findall(r'id="([^"]+)"', body))

    def tag(m):
        attrs, inner = m.group(1), m.group(2)
        if "id=" in attrs:
            hid = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            hid = base = slugify(inner)
            n = 2
            while hid in seen:
                hid, n = f"{base}-{n}", n + 1
            attrs = f'{attrs} id="{hid}"'
        seen.add(hid)
        items.append((hid, html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()))
        return f"<h2{attrs}>{inner}</h2>"

    return re.sub(r"<h2([^>]*)>(.*?)</h2>", tag, body, flags=re.S), items


def essay_page(p):
    f = frame(p["slug"])
    slug = p["slug"]
    question = f'<p class="essay-q">{q(f["question"])}</p>' if f["question"] else ""
    voices = (f'<p class="voices">Ideas from <b>{esc(", ".join(f["voices"]))}</b></p>' if f["voices"] else "")
    corrections = ""
    if f["corrections"]:
        items = "".join(f'<li><time datetime="{d}">{nice(d)}</time>: {esc(t)}</li>' for d, t in f["corrections"])
        corrections = f'<div class="corrections"><p class="label">Corrections</p><ul>{items}</ul></div>'
    after = []
    if f["sit"]:
        after.append(f'<aside class="sit-with" aria-labelledby="sit-h"><p class="label" id="sit-h">Sit with this</p>'
                     f'<p class="sit-q">{q(f["sit"])}</p></aside>')
    if f["related"]:
        r = post(f["related"])
        rq = frame(r["slug"])["question"] or r["title"]
        after.append(f'<nav class="read-next" aria-label="Read next"><p class="label">Read next</p>'
                     f'<a href="/blog/{r["slug"]}/"><span class="q-text">{q(rq)}</span><cite>{esc(r["title"])}</cite></a></nav>')
    after.append('<p class="disagree"><strong>Disagree? Good.</strong> Read the other side\'s best case too.</p>')
    body, parts = with_outline(body_of(slug))
    POST_BODIES.append(body)
    outline = ""
    if len(parts) >= 3:
        links = "".join(f'<li><a href="#{hid}">{html.escape(text)}</a></li>' for hid, text in parts)
        outline = f'<nav class="outline" aria-label="The argument"><p class="label">The argument</p><ol>{links}</ol></nav>'

    return f"""<div class="read-progress" aria-hidden="true"></div>
<article class="essay">
<header class="essay-head">
<a class="back" href="/blog/">← All questions</a>
<p class="label essay-kind">{esc(f["theme"])}{kind_badge(f["kind"])}</p>
{question}
<h1>{esc(p['title'])}</h1>
<p class="essay-meta"><time datetime="{p['date']}">{nice(p['date'])}</time> · {minutes(slug)} min read</p>
{voices}
{corrections}
</header>
<div class="essay-body">
<div class="prose">
{body}
</div>
{outline}
</div>
<div class="after">
{"".join(after)}
<p class="essay-end"><a class="back" href="/blog/">← All questions</a><a class="back" href="/how-i-argue/">How I argue here</a></p>
</div>
</article>
"""


def episode_card(e, full=True):
    overview = ""
    if full and e["overview"]:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    if e.get("listen_url"):
        player = f'<p class="player"><a href="{e["listen_url"]}" target="_blank" rel="noopener noreferrer">Listen on Speechify (opens in a new tab)</a></p>'
    else:
        player = f"""<div class="player"><audio controls preload="none" src="{e['audio']}" aria-label="{esc(e['title'])}"></audio></div>"""
    note = f'<p class="meta">{esc(e["note"])}</p>' if e.get("note") else ""
    question = EPISODE_QUESTIONS.get(e["slug"])
    asks = f'<p class="label">The question</p><p class="ep-q">{q(question)}</p>' if question else ""
    return f"""<section class="episode" id="{e['slug']}" aria-labelledby="{e['slug']}-h">
{asks}
<h2 id="{e['slug']}-h">{esc(e['title'])}</h2>
<p class="meta">{AUDIO_TAG}<time datetime="{e['date']}">{nice(e['date'])}</time> · {e['length']}</p>
<p>{esc(e['summary'])}</p>
{player}{note}
{overview}
</section>"""


def simple(kicker, h1, lede, inner):
    k = f'<p class="kicker">{kicker}</p>' if kicker else ""
    l = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<div class="page">
<header class="page-head">{k}<h1>{h1}</h1>{l}</header>
<div class="page-body">
{inner}
</div>
</div>
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "site.css", OUT / "site.css")
    shutil.copy(ROOT / "favicon.svg", OUT / "favicon.svg")
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    shutil.copytree(ROOT / "fonts", OUT / "fonts")
    (OUT / "CNAME").write_text("hoto.lol\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "ads.txt").write_text("google.com, pub-2462240112532447, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text("User-agent: Mediapartners-Google\nAllow: /\n\nUser-agent: *\nDisallow: /\n")

    for slug, f in FRAMING.items():
        assert any(p["slug"] == slug for p in POSTS), f"framing for unknown post {slug}"
        assert f["theme"] in THEMES, f"unknown theme for {slug}"
        assert not f.get("related") or any(p["slug"] == f["related"] for p in POSTS), f"bad related link in {slug}"

    desc = "An independent, personal journal of hard questions about society: essays, a podcast, and a private civic self-check."
    # The home page and /blog/ are the same front page. hoto.lol/ currently redirects to /blog/.
    write("index.html", page("/", None, HOME_DESC, front_page(), og=True))
    write("blog/index.html", page("/blog/", "Questions", desc, front_page()))

    for p in POSTS:
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], essay_page(p)))

    write("about/index.html", page("/about/", "About", "About this site.", simple(
        "About", "About", None, "<p>[Owner to write: a few sentences on who writes this site and why.]</p>")))

    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcast", "Podcast episodes: thinking out loud about hard questions.", simple(
        "Project Hoto podcast", "Podcast",
        "These episodes are personal reflections and opinions. They are conversation, not therapy. Nothing plays until you press Play.",
        cards)))

    shape = "".join(f"<li><div><b>{esc(a)}</b><span>{esc(b)}</span></div></li>" for a, b in [
        ("Why it matters", "Why this question is worth your time, and mine."),
        ("What we know", "What is documented, what is uncertain, and what I think, kept apart."),
        ("Who decides", "Who has the power to change it."),
        ("Who pays", "Who benefits, and who bears the costs."),
        ("Who gets missed", "Who falls through the cracks, and what it would take to reach them."),
        ("The best objection", "The strongest fair case against my view."),
        ("One change", "A specific proposal, its trade-offs, and how we would know if it helped."),
        ("Sources and corrections", "Every source, plus a dated note on anything I fixed."),
    ])
    rules = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in RULES)
    ideals = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in IDEALS)
    write("how-i-argue/index.html", page("/how-i-argue/", "How I argue here", "The rules this blog holds itself to.", simple(
        "The method", "How I argue here",
        "Project Hoto is one person thinking in public about hard questions. These are the rules I hold myself to, so you can tell where fact ends and opinion begins.",
        f"""<h2 id="ideals">Where I start from</h2>
<p>Five ideals sit under every question here. They come from a simple picture of a good community: when hard times hit, neighbors help each other through.</p>
<div class="rules-page">{ideals}</div>
<p>{IDEALS_CREDIT}</p>
<h2>Four commitments</h2>
<div class="rules-page">{rules}</div>
<h2>The shape of a question</h2>
<p>This is the order I am building new essays around. Each step answers something a fair reader would ask.</p>
<ol class="shape">{shape}</ol>
<h2>What this is not</h2>
<p>{UNOFFICIAL}</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p class="aside-note">{BLUNT}</p>
<p><a class="more" href="/blog/">← Back to the questions</a></p>""")))

    # Civic guide: a standalone page, deliberately NOT built with page(), so it never
    # loads the AdSense script. Its own CSP blocks all network requests. Political and
    # social-location answers must never reach ads, analytics, or storage.
    quiz = (ROOT / "civic" / "quiz.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in quiz and "adsbygoogle" not in quiz, "civic guide must not load ads"
    assert "connect-src 'none'" in quiz, "civic guide must keep its no-network CSP"
    plain_link = '<link rel="stylesheet" href="/site.css">'
    assert quiz.count(plain_link) == 1, "civic guide should link /site.css exactly once"
    write("civic/index.html", quiz.replace(plain_link, CSS_LINK))

    # Privacy
    write("privacy/index.html", page("/privacy/", "Privacy", "How this site handles your data and ads.", simple(
        None, "Privacy", None, """<p>No accounts. No forms. Nothing you type here is sent to this site.</p>
<h2>Ads</h2>
<p>This site does not currently show ads. If that changes, this page will be updated before any ads appear.</p>
<h2>Civic guide</h2>
<p>The <a href="/civic/">civic guide</a> has no ads, trackers, or analytics. It blocks all network requests, so your answers cannot be sent anywhere. Answers are kept only in the open page, never saved to your browser, and disappear when you leave or press “Reset all answers.” Your political answers are never used for ads, accounts, or retargeting.</p>
<h2>Podcast audio</h2>
<p>Episodes are hosted on this site and only load when you press Play.</p>
<h2>Fonts</h2>
<p>The fonts are stored on this site too. Showing text never contacts a font service or any other outside server.</p>""")))

    # 404
    write("404.html", page("/404", "Not found", "Page not found.", simple(
        None, 'Nothing here<span class="qm">?</span>', None,
        '<p>That page does not exist, or it moved.</p>'
        '<p class="actions"><a class="cta" href="/blog/">Go to the questions</a></p>')))


CRISIS = ('In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.')
FOOTER_LINES = [
    "Independent and unofficial. Not affiliated with any politician, party, campaign, or government.",
    "Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.",
    'This site currently shows no ads. <a href="/privacy/">Privacy</a>.',
]
# The civic guide is a standalone page with its own two-line footer, written for its no-ads, no-network promise.
OWN_FOOTER = {"civic/index.html"}
EXTERNAL_ASSET = re.compile(r'<(?:link|script|img)\b[^>]*?\b(?:src|href)\s*=\s*["\']?(?:https?:)?//', re.I)
PLACEHOLDER = re.compile(r"\[(?:[A-Z]|\d+|TODO|TBD|XX+|\.\.\.|insert[^\]]*|placeholder[^\]]*)\]", re.I)


def check_output():
    """Fail the build on mistakes that are easy to ship and hard to see."""
    errors = []
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT).as_posix()
        text = f.read_text(encoding="utf-8")
        rest = text
        for b in POST_BODIES:
            rest = rest.replace(b, "")
        if "\u2014" in rest:
            errors.append(f"{rel}: em dash outside an essay body")
        if m := EXTERNAL_ASSET.search(text):
            errors.append(f"{rel}: external URL in a link, script or img tag: {m.group(0)[:80]}")
        if CRISIS not in text:
            errors.append(f"{rel}: crisis strip text is missing or changed")
        if rel not in OWN_FOOTER:
            errors += [f"{rel}: footer line missing: {line[:40]}" for line in FOOTER_LINES if f"<p>{line}</p>" not in text]
        if m := PLACEHOLDER.search(re.sub(r"<(script|style)\b.*?</\1>", "", rest, flags=re.S)):
            errors.append(f"{rel}: leftover placeholder text {m.group(0)}")
    if errors:
        raise SystemExit("Build checks failed:\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    build()
    check_output()
    print("Built", sum(1 for _ in OUT.rglob("*.html")), "pages into", OUT)
