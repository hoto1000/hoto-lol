#!/usr/bin/env python3
"""Checks the built site in docs/. Run after build.py: python3 scripts/check_site.py

Standard library only, no network. Exits 1 if any check fails.
Notes (not failures): future-dated posts are reported as WARN, since dates are editorial.
"""
import datetime
import hashlib
import importlib.util
import pathlib
import re
import sys

sys.dont_write_bytecode = True
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

spec = importlib.util.spec_from_file_location("build", ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)  # build() only runs under __main__, so this just loads data

CRISIS = 'In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.'
STANDALONE = "civic/index.html"  # copied from civic/quiz.html: own CSP, own styles, no site.css
SCRIPTS_ALLOWED = {STANDALONE: 1}  # script tags that already exist; anything else fails
VOID = {"meta", "link", "br", "img", "hr", "input", "source", "area", "base", "col", "embed", "wbr", "track", "param"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.metas, self.links, self.a, self.ids = [], [], [], []
        self.tags, self.headings, self.src = {}, [], []
        self.stack, self.in_time, self.times, self.crisis_blocks = [], False, [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "a":
            self.a.append(a)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        elif tag == "time":
            self.times.append(a.get("datetime", ""))
        if tag in ("script", "img", "iframe", "source", "audio", "video", "embed", "object") and a.get("src"):
            self.src.append((tag, a["src"]))

    def meta(self, name):
        return [m.get("content", "") for m in self.metas if m.get("name") == name]


def external(url):
    return bool(re.match(r"(?:https?:)?//", url or "", re.I))


def target_file(base_rel, href):
    """Map an internal href to a file under docs/, or None if it leaves the site."""
    u = urlsplit(href)
    if u.scheme or u.netloc:
        return None
    path = unquote(u.path)
    if not path:
        return DOCS / base_rel
    p = (DOCS / path.lstrip("/")) if path.startswith("/") else (DOCS / base_rel).parent / path
    p = pathlib.Path(p.as_posix())
    return p / "index.html" if p.is_dir() or path.endswith("/") else p


def main():
    errors, warns = [], []
    err = lambda rel, msg: errors.append(f"{rel}: {msg}")
    pages = {}
    for f in sorted(DOCS.rglob("*.html")):
        rel = f.relative_to(DOCS).as_posix()
        text = f.read_text(encoding="utf-8")
        p = Page()
        p.feed(text)
        pages[rel] = (text, p)

    css = (ROOT / "site.css").read_bytes()
    css_version = hashlib.sha256(css).hexdigest()[:10]
    if css_version != build.CSS_VERSION:
        err("build.py", f"CSS_VERSION {build.CSS_VERSION} does not match site.css hash {css_version}")
    if (DOCS / "site.css").read_bytes() != css:
        err("site.css", "docs/site.css differs from site.css (rebuild)")
    want_link = f'<link rel="stylesheet" href="/site.css?v={css_version}">'

    for rel, (text, p) in pages.items():
        # crisis strip
        if CRISIS not in text:
            err(rel, "crisis strip text missing or not byte-exact")
        # meta
        if "noindex, nofollow" not in p.meta("robots"):
            err(rel, 'robots meta "noindex, nofollow" missing')
        if not p.meta("referrer"):
            err(rel, "referrer meta missing")
        if not p.meta("google-adsense-account"):
            (warns if rel == STANDALONE else errors).append(f"{rel}: google-adsense-account meta missing"
                                                            + (" (standalone civic page; reported, not changed)" if rel == STANDALONE else ""))
        # scripts, off-site loads, iframes
        n = p.tags.get("script", 0)
        if n != SCRIPTS_ALLOWED.get(rel, 0):
            err(rel, f"{n} script tag(s), expected {SCRIPTS_ALLOWED.get(rel, 0)}")
        if p.tags.get("iframe"):
            err(rel, "iframe present")
        for tag, s in p.src:
            if external(s):
                err(rel, f"<{tag} src> goes to another host: {s}")
        for l in p.links:
            if external(l.get("href")):
                err(rel, f"<link href> goes to another host: {l['href']}")
        # structure
        if p.tags.get("main", 0) != 1:
            err(rel, f"{p.tags.get('main', 0)} main elements, expected 1")
        if rel == STANDALONE:
            # the quiz writes its headings from a script, so count them in the source instead
            n1 = len(re.findall(r"<h1\b", text))
            if n1 != 1:
                err(rel, f"{n1} h1 in source, expected 1")
            else:
                warns.append(f"{rel}: its one h1 is written by the page script, not present in static HTML (reported, not changed)")
        elif p.headings.count(1) != 1:
            err(rel, f"{p.headings.count(1)} h1 elements, expected 1")
        for prev, cur in zip(p.headings, p.headings[1:] if rel != STANDALONE else []):
            if cur > prev + 1:
                err(rel, f"heading level skips from h{prev} to h{cur}")
                break
        dup = sorted({i for i in p.ids if p.ids.count(i) > 1})
        if dup:
            err(rel, f"duplicate ids: {', '.join(dup)}")
        # stylesheet
        sheets = [l for l in p.links if l.get("rel") == "stylesheet"]
        if rel == STANDALONE:
            hrefs = [l.get("href", "") for l in sheets]
            if "/site.css" not in hrefs and want_link.split('href="')[1].rstrip('">') not in hrefs:
                err(rel, "civic page does not link the shared stylesheet")
            elif "/site.css" in hrefs:
                warns.append(f"{rel}: links /site.css without the ?v= hash (reported, not changed)")
        elif want_link not in text:
            err(rel, f"stylesheet link is not {want_link}")
        # links
        for a in p.a:
            href = a.get("href")
            if href is None or external(href) or href.startswith(("mailto:", "tel:", "javascript:")):
                if a.get("target") == "_blank" and "noopener" not in a.get("rel", "") and external(href):
                    err(rel, f"target=_blank without rel noopener: {href}")
                continue
            frag = urlsplit(href).fragment
            tf = target_file(rel, href)
            if tf is None or not tf.is_file():
                err(rel, f"internal link does not resolve: {href}")
                continue
            if frag:
                trel = tf.relative_to(DOCS).as_posix()
                if trel.endswith(".html") and frag not in pages[trel][1].ids:
                    err(rel, f"fragment #{frag} not found in {trel}: {href}")
        for a in p.a:
            if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                err(rel, f"target=_blank without rel noopener: {a.get('href')}")
    # internal src/href of other assets (css, favicon, audio) must exist
    for rel, (text, p) in pages.items():
        for l in p.links:
            h = l.get("href", "")
            if h and not external(h):
                tf = target_file(rel, h)
                if tf is None or not tf.is_file():
                    err(rel, f"<link href> does not resolve: {h}")

    # posts agree with POSTS
    today = datetime.date.today().isoformat()
    for post in build.POSTS:
        rel = f"blog/{post['slug']}/index.html"
        if rel not in pages:
            err(rel, "post page missing")
            continue
        text, p = pages[rel]
        want_title = f"{build.esc(post['title'])} · {build.SITE}"
        m = re.search(r"<title>(.*?)</title>", text, re.S)
        if not m or m.group(1) != want_title:
            err(rel, f"title {m.group(1) if m else None!r} != {want_title!r}")
        h1 = re.search(r"<h1>(.*?)</h1>", text, re.S)
        if not h1 or h1.group(1) != build.esc(post["title"]):
            err(rel, "h1 does not match POSTS title")
        d = p.meta("description")
        if d != [post["summary"]]:
            err(rel, f"description meta {d!r} != POSTS summary")
        if not d or not d[0].strip() or len(d[0]) < 40:
            err(rel, "description meta missing or too short")
        if post["date"] not in p.times:
            err(rel, f"time element dates {p.times} do not include POSTS date {post['date']}")
        elif p.times[0] != post["date"]:
            err(rel, f"first time element {p.times[0]} != POSTS date {post['date']}")
        try:
            datetime.date.fromisoformat(post["date"])
        except ValueError:
            err(rel, f"POSTS date {post['date']!r} is not a valid date")
        if post["date"] > today:
            warns.append(f"{rel}: dated {post['date']}, later than today ({today}); reported, not changed")
        # the index listing should carry the same title and date
        for idx in ("index.html", "blog/index.html"):
            t = pages[idx][0]
            if f'href="/blog/{post["slug"]}/"' not in t:
                err(idx, f"does not list {post['slug']}")

    for w in warns:
        print("WARN", w)
    for e in errors:
        print("FAIL", e)
    print(f"{len(pages)} pages checked, {len(errors)} failure(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
