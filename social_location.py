"""The social location interview on /social-location/ and the question on the homepage.

No script and no form: every answer is a checkbox or radio button that stays in the open page.
Nothing is typed, saved or sent. The "Your map" summary is pure CSS: each choice has a line in
the map that only shows while that box is ticked (generated rules, appended to site.css at build).
"""
import html
import re

esc = html.escape

# (level id, level title, plain meaning, steps). Each step: (step id, question, kind, choices).
# kind "radio" = pick one, "check" = pick any.
LEVELS = [
    ("micro", "Micro", "you", [
        ("gen", "Which generation are you part of?", "radio",
         ["Gen Z (born 1997 to 2012)", "Millennial (born 1981 to 1996)", "Gen X (born 1965 to 1980)",
          "Baby Boomer (born 1946 to 1964)", "Silent Generation (born before 1946)"]),
        ("race", "How do you describe your race or ethnicity?", "check",
         ["Asian", "Black or African American", "Hispanic or Latino", "Middle Eastern or North African",
          "American Indian or Alaska Native", "Native Hawaiian or Pacific Islander", "White", "Multiracial", "Another"]),
        ("gender", "How do you describe your gender?", "check",
         ["Woman", "Man", "Nonbinary", "Transgender", "Another", "Still figuring it out"]),
        ("orient", "How do you describe your sexual orientation?", "check",
         ["Straight", "Gay", "Lesbian", "Bisexual", "Queer", "Asexual", "Another", "Still figuring it out"]),
        ("faith", "What about religion or spirituality?", "check",
         ["Christian", "Muslim", "Jewish", "Buddhist", "Hindu", "Sikh", "Folk or ancestral traditions",
          "Spiritual but not religious", "Not religious", "Another"]),
        ("ability", "Do you live with a disability or a long-term health condition?", "check",
         ["Yes, since I was young", "Yes, it started later in life", "Not that I know of", "Not sure"]),
        ("class-then", "Growing up, how did money feel at home?", "radio",
         ["Very tight", "We got by", "Comfortable", "Wealthy"]),
        ("class-now", "How does money feel now?", "radio",
         ["Very tight", "I get by", "Comfortable", "Wealthy"]),
        ("origin", "What's your family's migration story?", "check",
         ["Born in the country I live in", "Moved here as a child", "Moved here as an adult",
          "Child of immigrants", "Grandchild of immigrants", "Refugee background"]),
        ("indig", "Do you have Indigenous heritage?", "radio", ["Yes", "No", "Not sure"]),
        ("lang", "What language did you hear at home?", "radio",
         ["Only English", "Another language", "More than one language"]),
    ]),
    ("meso", "Meso", "your communities", [
        ("week", "Where do you spend most of your week?", "check",
         ["School", "Work", "Home, caring for family", "A place of worship", "A team or club",
          "Online communities", "Looking for work"]),
        ("grew", "Where did you grow up?", "check",
         ["A big city", "A suburb", "A small town", "A rural area", "We moved around a lot"]),
        ("lean", "Who do you lean on?", "check",
         ["Family", "Friends", "Chosen family", "A partner", "A faith community", "Coworkers or classmates",
          "A therapist or counselor", "Mostly myself"]),
        ("belong", "Where do you feel like you belong?", "check",
         ["Home", "School", "Work", "A place of worship", "My neighborhood", "Online", "Nowhere yet"]),
    ]),
    ("macro", "Macro", "society", [
        ("events", "Which big events happened while you were growing up or since?", "check",
         ["9/11 and the wars after it", "The 2008 recession", "The COVID-19 pandemic",
          "The 2020 protests for racial justice", "Rising rent and housing costs",
          "A war or crisis in my family's home country"]),
        ("systems", "Which systems have touched your life or your family's?", "check",
         ["Immigration", "Healthcare and insurance", "Public schools", "Housing and rent", "Police or courts",
          "Food or cash assistance", "The military", "Foster care"]),
        ("messages", "Which messages about a good life did you grow up hearing?", "check",
         ["Go to college", "Own a home", "Make a lot of money", "Get married and have kids",
          "Take care of your parents", "Follow your faith", "Don't make trouble"]),
    ]),
]


# Short label shown before each pick in "Your map", so a line like "We got by" keeps its meaning.
MAP_LABEL = {"gen": "Generation", "race": "Race or ethnicity", "gender": "Gender", "orient": "Sexual orientation",
             "faith": "Religion", "ability": "Disability", "class-then": "Money growing up", "class-now": "Money now",
             "origin": "Migration", "indig": "Indigenous heritage", "lang": "Language at home",
             "week": "My week", "grew": "Grew up in", "lean": "I lean on", "belong": "I belong",
             "events": "Lived through", "systems": "Touched by", "messages": "Heard growing up"}


def _id(step, i):
    return f"sl-{step}-{i}"


def interview_html():
    """The interview steps, then the live map."""
    out = []
    for lid, title, meaning, steps in LEVELS:
        out.append(f'<section class="sl-level" id="{lid}" aria-labelledby="{lid}-h">'
                   f'<h2 id="{lid}-h"><span class="sl-tag">{title}</span> {esc(meaning.capitalize())}</h2>')
        for sid, q, kind, choices in steps:
            typ = "radio" if kind == "radio" else "checkbox"
            hint = "Pick one, or skip." if kind == "radio" else "Pick any that fit, or skip."
            chips = "".join(
                f'<label class="chip"><input type="{typ}" name="sl-{sid}" id="{_id(sid, i)}">{esc(c)}</label>'
                for i, c in enumerate(choices))
            out.append(f'<fieldset class="sl-step"><legend>{esc(q)}</legend><p class="sl-hint">{hint}</p>'
                       f'<div class="chips">{chips}</div></fieldset>')
        out.append("</section>")
    cols = []
    for lid, title, meaning, steps in LEVELS:
        items = "".join(f'<li class="sl-pick" data-pick="{_id(sid, i)}"><span class="sl-k">{MAP_LABEL[sid]}:</span> {esc(c)}</li>'
                        for sid, q, kind, choices in steps for i, c in enumerate(choices))
        cols.append(f'<div class="sl-col sl-col-{lid}"><h3><span class="sl-tag">{title}</span> {esc(meaning.capitalize())}</h3>'
                    f'<ul>{items}</ul><p class="sl-empty">Nothing picked yet.</p></div>')
    out.append('<section class="sl-map" id="your-map" aria-labelledby="map-h"><h2 id="map-h">Your map</h2>'
               '<p>Here is what you picked, at three levels. It lives only on this open page and is gone when you leave. '
               'To keep it, use your browser\'s Print option.</p>'
               f'<div class="sl-cols">{"".join(cols)}</div>'
               '<p class="sl-old">If your picks don\'t show up here, your browser is too old for this part. The questions above still work.</p>'
               '</section>')
    return "\n".join(out)


def interview_css():
    """One rule per choice: show its line in the map while its box is ticked."""
    shows = [f'main:has(#{_id(sid, i)}:checked) [data-pick="{_id(sid, i)}"]'
             for _, _, _, steps in LEVELS for sid, _, _, choices in steps for i in range(len(choices))]
    empties = [f'main:has(#{lid} input:checked) .sl-col-{lid} .sl-empty' for lid, _, _, _ in LEVELS]
    return ("\n/* Social location interview: generated by social_location.py, do not edit by hand. */\n"
            + ",\n".join(shows) + " { display: list-item; }\n"
            + ",\n".join(empties) + " { display: none; }\n")


HOME_ASK = """<section class="sl-ask" aria-labelledby="ask-h">
<h2 id="ask-h">Want to map your social location?</h2>
<p>A short interview, about five minutes. Pick the words that fit you and see your map at three levels: micro (you), meso (your communities), and macro (society). Nothing is saved or sent.</p>
<p class="btn-grid"><a class="btn btn-main" href="/social-location/#micro">Yes, start the interview</a><a class="btn" href="#latest">Not right now</a></p>
</section>"""


def choice_count():
    return sum(len(c) for _, _, _, steps in LEVELS for _, _, _, c in steps)


assert set(MAP_LABEL) == {sid for _, _, _, steps in LEVELS for sid, _, _, _ in steps}
assert all(re.fullmatch(r"[a-z-]+", sid) for _, _, _, steps in LEVELS for sid, _, _, _ in steps)


START = "/* BEGIN social-location generated */"
END = "/* END social-location generated */"


def css_block():
    return START + interview_css() + END


def sync_css(path):
    """Write the generated block into site.css. Run: python3 social_location.py"""
    text = path.read_text(encoding="utf-8")
    block = css_block()
    if START in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, text, flags=re.S)
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    import pathlib
    sync_css(pathlib.Path(__file__).parent / "site.css")
    print("site.css interview rules updated")
